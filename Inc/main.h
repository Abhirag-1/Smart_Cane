/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c firmware
  *                   STM32F103 GPS (Parsed Lat/Lon), HC-SR04 Ultrasonic,
  *                   and Latching/Momentary Emergency Button System.
  * @target         : STM32F103C8T6 (Blue Pill)
  * @toolchain      : Keil MDK / STM32CubeIDE / GCC ARM Embedded
  ******************************************************************************
  */

#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>

/* If compiled inside STM32CubeIDE or CMSIS environment, include standard header: */
#if defined(STM32F103xB) || defined(STM32F10X_MD) || defined(USE_HAL_DRIVER)
  #include "stm32f1xx.h"
#else
  /* Standalone CMSIS Register Definitions (No external dependencies needed) */
  #define PERIPH_BASE           (0x40000000UL)
  #define APB1PERIPH_BASE       (PERIPH_BASE)
  #define APB2PERIPH_BASE       (PERIPH_BASE + 0x10000UL)
  #define AHBPERIPH_BASE        (PERIPH_BASE + 0x20000UL)

  #define RCC_BASE              (AHBPERIPH_BASE + 0x1000UL)
  #define GPIOA_BASE            (APB2PERIPH_BASE + 0x0800UL)
  #define GPIOB_BASE            (APB2PERIPH_BASE + 0x0C00UL)
  #define GPIOC_BASE            (APB2PERIPH_BASE + 0x1000UL)
  #define USART1_BASE           (APB2PERIPH_BASE + 0x3800UL)
  #define USART2_BASE           (APB1PERIPH_BASE + 0x4400UL)
  #define TIM2_BASE             (APB1PERIPH_BASE + 0x0000UL)

  typedef struct {
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t APB2RSTR;
    volatile uint32_t APB1RSTR;
    volatile uint32_t AHBENR;
    volatile uint32_t APB2ENR;
    volatile uint32_t APB1ENR;
    volatile uint32_t BDCR;
    volatile uint32_t CSR;
  } RCC_TypeDef;

  typedef struct {
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
    volatile uint32_t LCKR;
  } GPIO_TypeDef;

  typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t CR3;
    volatile uint32_t GTPR;
  } USART_TypeDef;

  typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
  } TIM_TypeDef;

  typedef struct {
    volatile uint32_t CTRL;
    volatile uint32_t LOAD;
    volatile uint32_t VAL;
    volatile uint32_t CALIB;
  } SysTick_TypeDef;

  #define RCC                   ((RCC_TypeDef *) RCC_BASE)
  #define GPIOA                 ((GPIO_TypeDef *) GPIOA_BASE)
  #define GPIOB                 ((GPIO_TypeDef *) GPIOB_BASE)
  #define GPIOC                 ((GPIO_TypeDef *) GPIOC_BASE)
  #define USART1                ((USART_TypeDef *) USART1_BASE)
  #define USART2                ((USART_TypeDef *) USART2_BASE)
  #define TIM2                  ((TIM_TypeDef *) TIM2_BASE)
  #define SysTick               ((SysTick_TypeDef *) 0xE000E010UL)

  #ifndef __NOP
    #define __NOP()             __asm__ volatile ("nop")
  #endif
#endif

/* System Pin Configuration --------------------------------------------------*/
/* GPIOA */
#define PIN_TRIG              (1 << 0)   /* PA0: HC-SR04 Trigger (Output Push-Pull) */
#define PIN_ECHO              (1 << 1)   /* PA1: HC-SR04 Echo (Input Floating)      */
#define PIN_BT_TX             (1 << 2)   /* PA2: HC-05 RX via USART2 TX (AF Push-Pull) */
#define PIN_BT_RX             (1 << 3)   /* PA3: HC-05 TX via USART2 RX (Input Pull-up) */
#define PIN_GPS_TX            (1 << 9)   /* PA9: NEO-6M RX via USART1 TX (AF Push-Pull) */
#define PIN_GPS_RX            (1 << 10)  /* PA10: NEO-6M TX via USART1 RX (Input Pull-up) */

/* GPIOB */
#define PIN_EMERGENCY_BTN     (1 << 1)   /* PB1: Emergency SOS Button (Input Pull-up) */

/* GPIOC */
#define PIN_LED               (1 << 13)  /* PC13: Onboard LED (Active-LOW)          */

/* Timing & Threshold Parameters ---------------------------------------------*/
#define SYSCLK_FREQ_HZ        (8000000UL) /* 8 MHz internal HSI default */
#define GPS_STREAM_INTERVAL   (5000U)     /* GPS emitted every 5.0 seconds */
#define ULTRASONIC_INTERVAL   (100U)      /* Ping every 100 ms */
#define ALERT_COOLDOWN        (500U)      /* Min 500 ms between obstacle alerts */
#define SOS_CANCEL_WINDOW_MS  (5000U)     /* 5-second window for False Alarm cancel */
#define MOMENTARY_HOLD_MIN_MS (350U)      /* Threshold to distinguish latch vs tap */
#define BTN_DEBOUNCE_MS       (50U)       /* 50 ms button debounce */
#define GPS_JUMP_THRESHOLD_TENTHS (10U)   /* Jump filter: 10 tenths (~1.85 km in 5s) */

#define DISTANCE_ALERT_MAX_CM (50U)       /* Alert if distance <= 50 cm */
#define DISTANCE_ALERT_MIN_CM (2U)        /* Blind zone threshold (2 cm) */

/* System States -------------------------------------------------------------*/
typedef enum {
  EMERGENCY_STATE_NORMAL    = 0,  /* Normal operation: GPS 5s, Ultrasonic active */
  EMERGENCY_STATE_PENDING   = 1,  /* 1st button press: 5s countdown active       */
  EMERGENCY_STATE_CONFIRMED = 2   /* SOS confirmed: Ultrasonic OFF, GPS streaming*/
} EmergencyState_t;

typedef enum {
  GPS_STATE_IDLE      = 0,        /* Waiting for 5s timer trigger */
  GPS_STATE_WAIT_DOLLAR = 1,      /* Looking for start-of-sentence '$' */
  GPS_STATE_BUFFERING = 2         /* Buffering characters until '\n' */
} GpsState_t;

/* String Banners ------------------------------------------------------------*/
#define STR_BANNER \
  "\r\n=== STM32 GPS (Parsed Lat/Lon) & Ultrasonic Ready ===\r\n" \
  "[GPS]: 5-sec interval (Parsed)\r\n" \
  "[Ultrasonic]: Alert if <= 50 cm\r\n" \
  "[Emergency]: PB1 Button (Push 2x < 5s = False Alarm)\r\n\r\n"

#define STR_SOS_BANNER \
  "\r\n========================================\r\n" \
  "*** [EMERGENCY SITUATION WARNING] ***\r\n" \
  "*** SOS BUTTON PRESSED! ***\r\n" \
  "========================================\r\n"

#define STR_SOS_CONFIRMED \
  "\r\n*** [EMERGENCY CONFIRMED - SOS ACTIVE] ***\r\n"

#define STR_FALSE_ALARM \
  "\r\n========================================\r\n" \
  "*** [FALSE ALARM]: Pressed Again Within 5s ***\r\n" \
  "*** EMERGENCY CANCELLED - NORMAL RESUMED ***\r\n" \
  "========================================\r\n\r\n"

#define STR_SOS_CLEARED \
  "\r\n========================================\r\n" \
  "*** [EMERGENCY CLEARED - SOS OFF] ***\r\n" \
  "*** NORMAL MODE RESUMED ***\r\n" \
  "========================================\r\n\r\n"

#define STR_SOS_PREFIX \
  "\r\n*** [EMERGENCY GPS LOCATION] ***\r\n"

#define STR_ALERT_PRE     "\r\n[ALERT] Obstacle: "
#define STR_ALERT_POST    " cm\r\n"
#define STR_SEARCHING     "GPS: Searching for Satellites... (No Lock)\r\n"

/* Function Prototypes -------------------------------------------------------*/
void System_Init(void);
void UART2_SendChar(char c);
void UART2_SendString(const char *str);
void UART2_SendNum(uint32_t num);
void UART2_Send2DigitNum(uint32_t num);
bool Parse_RMC(char *line);
void Send_Parsed_GPS(void);
void Filter_And_Send_GPS(void);
void Process_Emergency_Button(void);
void Process_GPS_Byte(uint8_t byte);
void Process_SysTick(void);
void Process_Ultrasonic(void);

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
