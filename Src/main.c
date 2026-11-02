/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Complete C Implementation of the STM32F103 GPS,
  *                   Ultrasonic Proximity Alert, and Latching/Momentary
  *                   Emergency SOS System.
  * @target         : STM32F103C8T6 (ARM Cortex-M3 @ 8 MHz)
  * @peripherals    : USART1 (GPS @ 9600), USART2 (HC-05 BT @ 9600),
  *                   TIM2 (1us Echo Timer), SysTick (1ms System Tick),
  *                   HC-SR04 (PA0 Trig, PA1 Echo), PB1 Button, PC13 LED.
  ******************************************************************************
  */

#include "main.h"

/* Global Telemetry & System Variables ---------------------------------------*/
static volatile uint32_t ms_counter         = 0;
static volatile uint32_t gps_timer          = 0;
static volatile uint32_t ultrasonic_timer   = 0;
static volatile uint32_t alert_cooldown     = 0;

static volatile uint32_t emergency_state    = EMERGENCY_STATE_NORMAL;
static volatile uint32_t emergency_timer_ms = 0;

static volatile uint32_t last_btn_level     = 0;
static volatile uint32_t btn_idle_level     = 0;
static volatile uint32_t btn_debounce_timer = 0;
static volatile uint32_t btn_press_duration = 0;

static volatile uint32_t distance_cm        = 999;
static volatile uint32_t raw_echo_us        = 0;

/* GPS Receiver & Parser Variables -------------------------------------------*/
static volatile uint32_t gps_state          = GPS_STATE_WAIT_DOLLAR; /* Send GPS on boot */
static char line_buf[128];
static uint32_t line_buf_idx                = 0;

static char gps_status                      = 'V';
static char *ptr_lat                        = NULL;
static char ns_char                         = 'N';
static char *ptr_lon                        = NULL;
static char ew_char                         = 'E';

/* ---------------------------------------------------------------------------*/
/* Hardware Initialization                                                    */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Configures Clocks, GPIOs, SysTick, TIM2, USART1, and USART2.
  */
void System_Init(void) {
    /* 1. Clocks: APB2 (AFIO, IOPA, IOPB, IOPC, USART1) | APB1 (TIM2, USART2) */
    RCC->APB2ENR = 0x0000401D; /* AFIO(bit 0), IOPA(bit 2), IOPB(bit 3), IOPC(bit 4), USART1(bit 14) */
    RCC->APB1ENR = 0x00020001; /* TIM2(bit 0), USART2(bit 17) */

    /* 2. GPIOA:
     *    PA0  -> Output Push-Pull 2MHz (CNF=00, MODE=10 -> 0x2) [Trig]
     *    PA1  -> Input Floating        (CNF=01, MODE=00 -> 0x4) [Echo]
     *    PA2  -> Alternate Function PP (CNF=10, MODE=11 -> 0xB) [USART2 TX]
     *    PA3  -> Input with Pull-up    (CNF=10, MODE=00 -> 0x8) [USART2 RX]
     *    PA9  -> Alternate Function PP (CNF=10, MODE=11 -> 0xB) [USART1 TX]
     *    PA10 -> Input with Pull-up    (CNF=10, MODE=00 -> 0x8) [USART1 RX]
     */
    GPIOA->CRL = 0x44448B42;
    GPIOA->CRH = 0x444448B4;
    GPIOA->BSRR = (1 << 3) | (1 << 10); /* Pull-up on PA3 and PA10 */

    /* 3. GPIOB:
     *    PB1  -> Input with Pull-up    (CNF=10, MODE=00 -> 0x8) [Emergency Button]
     */
    GPIOB->CRL = 0x44444484;
    GPIOB->BSRR = (1 << 1);             /* Set ODR1 = 1 (Internal Pull-Up enabled) */

    /* Settle delay for pull-up resistor (~100 us) */
    for (volatile int i = 0; i < 200; i++) { __NOP(); }

    /* 4. GPIOC:
     *    PC13 -> Output Push-Pull 2MHz (CNF=00, MODE=10 -> 0x2) [Status LED]
     */
    GPIOC->CRH = 0x44244444;
    GPIOC->BSRR = (1 << 13);            /* Turn LED OFF initially (Active-LOW) */

    /* 5. SysTick Timer: 1ms tick @ 8 MHz (8000 ticks) */
    SysTick->LOAD = 7999;
    SysTick->VAL  = 0;
    SysTick->CTRL = 5;                  /* CLKSOURCE=1 (CPU), ENABLE=1 */

    /* 6. TIM2: Prescaler = 7 (1us tick @ 8 MHz), ARR = 0xFFFF */
    TIM2->PSC = 7;
    TIM2->ARR = 0xFFFF;
    TIM2->CR1 = 0;

    /* 7. USART1 (NEO-6M GPS @ 9600 baud, 8-N-1) */
    USART1->CR1 = 0;
    USART1->BRR = 0x0341;               /* 8MHz / (16 * 9600) = 52.083 -> 0x0341 */
    USART1->CR1 = 0x200C;               /* UE=1, TE=1, RE=1 */

    /* 8. USART2 (HC-05 Bluetooth @ 9600 baud, 8-N-1) */
    USART2->CR1 = 0;
    USART2->BRR = 0x0341;
    USART2->CR1 = 0x200C;

    /* 9. Sample initial PB1 button level */
    uint32_t initial_pin = (GPIOB->IDR >> 1) & 0x01;
    last_btn_level = initial_pin;
    btn_idle_level = initial_pin;

    /* Transmit Welcome Banner to Bluetooth */
    UART2_SendString(STR_BANNER);
}

/* ---------------------------------------------------------------------------*/
/* UART Helper Functions                                                      */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Transmits a single character over USART2 (HC-05).
  */
void UART2_SendChar(char c) {
    while (!(USART2->SR & (1 << 7))) {
        /* Wait until TXE (Transmit Data Register Empty) */
    }
    USART2->DR = (uint8_t)c;
}

/**
  * @brief  Transmits a null-terminated string over USART2 (HC-05).
  */
void UART2_SendString(const char *str) {
    while (*str) {
        UART2_SendChar(*str++);
    }
}

/**
  * @brief  Transmits a 2-digit decimal number (00..99) over USART2.
  */
void UART2_Send2DigitNum(uint32_t num) {
    uint8_t tens = (uint8_t)(num / 10);
    uint8_t units = (uint8_t)(num % 10);
    UART2_SendChar((char)('0' + tens));
    UART2_SendChar((char)('0' + units));
}

/* ---------------------------------------------------------------------------*/
/* GPS NMEA RMC Sentence Parser                                               */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Validates and parses $GPRMC / $GNRMC sentences.
  *         Extracts Fix Status, Latitude, N/S, Longitude, and E/W pointers.
  * @param  line: Null-terminated NMEA sentence string.
  * @retval true if valid RMC sentence parsed, false otherwise.
  */
bool Parse_RMC(char *line) {
    /* Verify sentence starts with '$', has 'R', 'M', 'C' at indices 3, 4, 5 */
    if (line[0] != '$' || line[3] != 'R' || line[4] != 'M' || line[5] != 'C') {
        return false;
    }

    uint32_t comma_count = 0;
    char *p = line;

    while (*p != '\0') {
        if (*p == ',') {
            comma_count++;
            switch (comma_count) {
                case 2:
                    /* Comma 2: Status character follows ('A' = Valid, 'V' = Warning) */
                    gps_status = *(p + 1);
                    break;

                case 3:
                    /* Comma 3: Start of Latitude field */
                    ptr_lat = p + 1;
                    break;

                case 4:
                    /* Comma 4: Null-terminate Lat string, read N/S */
                    *p = '\0';
                    ns_char = *(p + 1);
                    break;

                case 5:
                    /* Comma 5: Start of Longitude field */
                    ptr_lon = p + 1;
                    break;

                case 6:
                    /* Comma 6: Null-terminate Lon string, read E/W */
                    *p = '\0';
                    ew_char = *(p + 1);
                    break;

                case 7:
                    /* Finished extracting essential coordinates */
                    return true;

                default:
                    break;
            }
        }
        p++;
    }

    return (comma_count >= 6);
}

/**
  * @brief  Formats and transmits the parsed GPS location over HC-05.
  */
void Send_Parsed_GPS(void) {
    /* If emergency is active, send emergency header */
    if (emergency_state != EMERGENCY_STATE_NORMAL) {
        UART2_SendString(STR_SOS_PREFIX);
    }

    /* Check if satellite fix is valid ('A') */
    if (gps_status == 'A' && ptr_lat != NULL && ptr_lon != NULL) {
        UART2_SendString("Lat: ");
        UART2_SendString(ptr_lat);
        UART2_SendChar(' ');
        UART2_SendChar(ns_char);

        UART2_SendString(", Lon: ");
        UART2_SendString(ptr_lon);
        UART2_SendChar(' ');
        UART2_SendChar(ew_char);

        UART2_SendChar('\r');
        UART2_SendChar('\n');
    } else {
        UART2_SendString(STR_SEARCHING);
    }
}

/* ---------------------------------------------------------------------------*/
/* Emergency SOS Button State Machine (Universal Latching & Momentary Engine) */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Evaluates PB1 emergency button with debounce, supporting both
  *         latching toggle switches and momentary push buttons.
  */
void Process_Emergency_Button(void) {
    if (btn_debounce_timer > 0) {
        return; /* In debounce cooldown */
    }

    /* Read current PB1 level */
    uint32_t current_level = (GPIOB->IDR >> 1) & 0x01;

    if (current_level == last_btn_level) {
        return; /* Level has not changed */
    }

    /* State changed! Record new level and set 50ms debounce */
    last_btn_level = current_level;
    btn_debounce_timer = BTN_DEBOUNCE_MS;

    /* Determine transition direction */
    if (current_level != btn_idle_level) {
        /* ===================================================================
         * TRANSITION: IDLE -> ACTIVE (Button Pressed / Latched Active)
         * =================================================================== */
        btn_press_duration = 0;

        if (emergency_state == EMERGENCY_STATE_NORMAL) {
            /* PUSH 1: TRIGGER EMERGENCY! */
            emergency_state = EMERGENCY_STATE_PENDING;
            emergency_timer_ms = 0;

            UART2_SendString(STR_SOS_BANNER);

            /* Force immediate GPS reading and transmission */
            gps_timer = GPS_STREAM_INTERVAL;
            gps_state = GPS_STATE_WAIT_DOLLAR;
        }
        else if (emergency_state == EMERGENCY_STATE_PENDING) {
            /* 2ND PUSH WITHIN 5 SECONDS -> FALSE ALARM! */
            emergency_state = EMERGENCY_STATE_NORMAL;
            emergency_timer_ms = 0;

            UART2_SendString(STR_FALSE_ALARM);
        }
        else if (emergency_state == EMERGENCY_STATE_CONFIRMED) {
            /* 2ND PUSH AFTER 5 SECONDS -> EMERGENCY CLEARED! */
            emergency_state = EMERGENCY_STATE_NORMAL;
            emergency_timer_ms = 0;

            UART2_SendString(STR_SOS_CLEARED);
        }
    } else {
        /* ===================================================================
         * TRANSITION: ACTIVE -> IDLE (Button Released / Latched Normal)
         * =================================================================== */
        if (btn_press_duration < MOMENTARY_HOLD_MIN_MS) {
            /* Quick finger release (<350ms) on a momentary button -> Ignore release! */
            return;
        }

        /* Latching button stayed active for >= 350ms and now unlatched (2nd Press) */
        if (emergency_state == EMERGENCY_STATE_PENDING) {
            emergency_state = EMERGENCY_STATE_NORMAL;
            emergency_timer_ms = 0;
            UART2_SendString(STR_FALSE_ALARM);
        }
        else if (emergency_state == EMERGENCY_STATE_CONFIRMED) {
            emergency_state = EMERGENCY_STATE_NORMAL;
            emergency_timer_ms = 0;
            UART2_SendString(STR_SOS_CLEARED);
        }
    }
}

/* ---------------------------------------------------------------------------*/
/* GPS Serial Stream Handler                                                  */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Consumes incoming GPS bytes from USART1 DR and executes state machine.
  */
void Process_GPS_Byte(uint8_t byte) {
    if (gps_state == GPS_STATE_IDLE) {
        return; /* Discard bytes when idle */
    }

    if (gps_state == GPS_STATE_WAIT_DOLLAR) {
        if (byte == '$') {
            gps_state = GPS_STATE_BUFFERING;
            line_buf_idx = 0;
            line_buf[line_buf_idx++] = '$';
        }
        return;
    }

    if (gps_state == GPS_STATE_BUFFERING) {
        if (line_buf_idx < (sizeof(line_buf) - 2)) {
            line_buf[line_buf_idx++] = (char)byte;
        } else {
            /* Buffer overflow prevention: reset to idle */
            gps_state = GPS_STATE_IDLE;
            return;
        }

        if (byte == '\n') {
            line_buf[line_buf_idx] = '\0'; /* Null-terminate */

            if (Parse_RMC(line_buf)) {
                /* Successfully parsed $GPRMC / $GNRMC: Send formatted Lat/Lon */
                Send_Parsed_GPS();
                gps_state = GPS_STATE_IDLE; /* Done, rest until next 5s tick */
            } else {
                /* Not RMC: continue waiting for next sentence in the 1-second burst */
                gps_state = GPS_STATE_WAIT_DOLLAR;
            }
        }
    }
}

/* ---------------------------------------------------------------------------*/
/* SysTick Millisecond Timer Engine                                           */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Polls the SysTick COUNTFLAG (bit 16). When 1ms has elapsed,
  *         updates all software timers, emergency countdown, and LED.
  */
void Process_SysTick(void) {
    if (!(SysTick->CTRL & (1 << 16))) {
        return; /* 1ms has not yet elapsed */
    }

    ms_counter++;
    gps_timer++;
    ultrasonic_timer++;
    alert_cooldown++;
    btn_press_duration++;

    if (btn_debounce_timer > 0) {
        btn_debounce_timer--;
    }

    /* Handle 5-second Emergency Confirmation Countdown */
    if (emergency_state == EMERGENCY_STATE_PENDING) {
        emergency_timer_ms++;
        if (emergency_timer_ms >= SOS_CANCEL_WINDOW_MS) {
            /* 5 SECONDS REACHED WITHOUT CANCELLATION -> CONFIRMED EMERGENCY! */
            emergency_state = EMERGENCY_STATE_CONFIRMED;
            UART2_SendString(STR_SOS_CONFIRMED);
        }
    }

    /* Handle PC13 Status LED */
    if (emergency_state != EMERGENCY_STATE_NORMAL) {
        /* Emergency Active: Rapid Strobe (Toggle every ~128ms via bit 7) */
        if (ms_counter & 0x80) {
            GPIOC->BSRR = (1 << 29); /* BR13: LED ON */
        } else {
            GPIOC->BSRR = (1 << 13); /* BS13: LED OFF */
        }
    }

    /* Check GPS 5-Second Trigger */
    if (gps_timer >= GPS_STREAM_INTERVAL) {
        gps_timer = 0;
        if (gps_state == GPS_STATE_IDLE) {
            gps_state = GPS_STATE_WAIT_DOLLAR; /* Arm capture of next NMEA sentence */
        }
    }
}

/* ---------------------------------------------------------------------------*/
/* HC-SR04 Ultrasonic Distance Sensor Engine                                  */
/* ---------------------------------------------------------------------------*/

/**
  * @brief  Performs non-blocking check and triggers HC-SR04 sensor every 100ms.
  *         HALTED completely when an emergency is active.
  */
void Process_Ultrasonic(void) {
    /* CRITICAL: HALT ULTRASONIC SENSOR WHILE IN EMERGENCY MODE! */
    if (emergency_state != EMERGENCY_STATE_NORMAL) {
        return;
    }

    if (ultrasonic_timer < ULTRASONIC_INTERVAL) {
        return;
    }

    ultrasonic_timer = 0;

    /* 1. Generate 20us Trigger pulse on PA0 */
    GPIOA->BSRR = (1 << 0); /* PA0 HIGH */
    for (volatile int i = 0; i < 50; i++) { __NOP(); }
    GPIOA->BRR = (1 << 0);  /* PA0 LOW */

    /* 2. Wait for Echo (PA1) to go HIGH (Timeout ~35,000 iterations / ~25ms) */
    uint32_t timeout = 35000;
    while (!(GPIOA->IDR & (1 << 1))) {
        if (--timeout == 0) {
            distance_cm = 999; /* Echo never went high */
            GPIOC->BSRR = (1 << 13); /* LED OFF */
            return;
        }
    }

    /* 3. Echo went HIGH: Start TIM2 (1us tick) */
    TIM2->CNT = 0;
    TIM2->CR1 = 1; /* CEN = 1 (Enable counter) */

    /* 4. Wait for Echo (PA1) to go LOW (Timeout ~45,000 us) */
    while (GPIOA->IDR & (1 << 1)) {
        if (TIM2->CNT >= 45000) {
            TIM2->CR1 = 0; /* Stop counter */
            distance_cm = 999; /* Open-air timeout */
            GPIOC->BSRR = (1 << 13); /* LED OFF */
            return;
        }
    }

    /* 5. Echo dropped LOW: Stop TIM2 and read pulse duration */
    TIM2->CR1 = 0;
    raw_echo_us = TIM2->CNT;

    /* Ignore blind zone glitch (< 116 us / < 2 cm) */
    if (raw_echo_us < 116) {
        return;
    }

    /* Distance in cm = microseconds / 58 */
    distance_cm = raw_echo_us / 58;

    /* Check proximity threshold: 2 cm <= distance < 50 cm */
    if (distance_cm >= DISTANCE_ALERT_MIN_CM && distance_cm < DISTANCE_ALERT_MAX_CM) {
        /* Obstacle Detected: Turn PC13 LED ON (BR13) */
        GPIOC->BSRR = (1 << 29);

        /* Transmit obstacle alert if cooldown has expired (min 500ms) */
        if (alert_cooldown >= ALERT_COOLDOWN) {
            alert_cooldown = 0;
            UART2_SendString(STR_ALERT_PRE);
            UART2_Send2DigitNum(distance_cm);
            UART2_SendString(STR_ALERT_POST);
        }
    } else {
        /* Obstacle Cleared: Turn PC13 LED OFF (BS13) */
        GPIOC->BSRR = (1 << 13);
    }
}

/* ---------------------------------------------------------------------------*/
/* Main Program Loop                                                          */
/* ---------------------------------------------------------------------------*/

int main(void) {
    /* Initialize clocks, GPIOs, SysTick, TIM2, and UARTs */
    System_Init();

    /* Infinite Superloop */
    while (1) {
        /* 1. Process Emergency SOS Button */
        Process_Emergency_Button();

        /* 2. Process Incoming GPS Byte if available */
        if (USART1->SR & (1 << 5)) { /* RXNE (Read data register not empty) */
            uint8_t rx_byte = (uint8_t)(USART1->DR & 0xFF);
            Process_GPS_Byte(rx_byte);
        }

        /* 3. Process SysTick Timers and Countdowns */
        Process_SysTick();

        /* 4. Process Ultrasonic HC-SR04 Sensing (only in Normal Mode) */
        Process_Ultrasonic();
    }
}