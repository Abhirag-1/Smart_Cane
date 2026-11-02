
/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : STM32 Smart Cane - Without MPU6050
  *
  * HC-SR04 : PA0 / PA1
  * Motor   : PB0
  * Button  : PB1
  * GPS     : USART1 (PA9 / PA10)
  * HC-05   : USART2 (PA2 / PA3)
  * Timer   : TIM2
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/

#include "main.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* Private defines -----------------------------------------------------------*/

#define GPS_BUFFER_SIZE          128

#define OBSTACLE_LIMIT_CM        100.0f

#define ULTRASONIC_TIMEOUT_MS    30

#define MOTOR_ON_TIME_MS         120
#define MOTOR_OFF_TIME_MS        400

#define BUTTON_DEBOUNCE_MS       40

/* Private variables ---------------------------------------------------------*/

/* GPS */

uint8_t gpsRxByte;

char gpsBuffer[GPS_BUFFER_SIZE];
char gpsLine[GPS_BUFFER_SIZE];

volatile uint16_t gpsIndex = 0;
volatile uint8_t gpsLineReady = 0;

float latitude = 0.0f;
float longitude = 0.0f;

uint8_t gpsFix = 0;

/* Ultrasonic sensor */

float distanceCM = -1.0f;

uint8_t obstacleDetected = 0;

uint32_t lastUltrasonicTime = 0;

/* Motor */

uint8_t motorState = 0;

uint32_t motorTimer = 0;

/* Emergency button */

uint8_t buttonLastReading = 1;
uint8_t buttonStableState = 1;

uint32_t buttonDebounceTimer = 0;

/* Function prototypes -------------------------------------------------------*/

void SystemClock_Config(void);

static void GPS_StartReception(void);
static void GPS_ProcessLine(char *line);
static float GPS_ConvertToDecimal(double coordinate, char direction);

static float Ultrasonic_ReadDistance(void);

static void Motor_Update(void);

static void Button_Process(void);

static void Bluetooth_Send(const char *message);
static void Send_GPS_Location(const char *alert);
static void Send_Emergency_Alert(void);

/* Main program --------------------------------------------------------------*/

int main(void)
{
    HAL_Init();

    SystemClock_Config();

    /* Initialize peripherals */

    MX_GPIO_Init();
    MX_TIM2_Init();
    MX_USART1_UART_Init();
    MX_USART2_UART_Init();

    /* Start TIM2 */

    if (HAL_TIM_Base_Start(&htim2) != HAL_OK)
    {
        Error_Handler();
    }

    /* Motor OFF at startup */

    MOTOR_OFF();

    /* Start GPS reception */

    GPS_StartReception();

    /* Startup messages */

    Bluetooth_Send("\r\nSMART CANE STARTED\r\n");

    Bluetooth_Send("HC-05 READY\r\n");

    Bluetooth_Send("GPS INITIALIZING\r\n");

    Bluetooth_Send("OBSTACLE DETECTION READY\r\n");

    /* Main loop */

    while (1)
    {
        uint32_t currentTime = HAL_GetTick();

        /* ------------------------------------------------
           1. GPS PROCESSING
           ------------------------------------------------ */

        if (gpsLineReady)
        {
            __disable_irq();

            memcpy(gpsLine, gpsBuffer, GPS_BUFFER_SIZE);

            gpsLineReady = 0;
            gpsIndex = 0;

            __enable_irq();

            GPS_ProcessLine(gpsLine);
        }

        /* ------------------------------------------------
           2. ULTRASONIC SENSOR
           ------------------------------------------------ */

        if ((currentTime - lastUltrasonicTime) >= 100)
        {
            lastUltrasonicTime = currentTime;

            distanceCM = Ultrasonic_ReadDistance();

            if (distanceCM > 0.0f &&
                distanceCM < OBSTACLE_LIMIT_CM)
            {
                if (!obstacleDetected)
                {
                    obstacleDetected = 1;

                    char message[60];

                    snprintf(message,
                             sizeof(message),
                             "OBSTACLE DETECTED: %.1f CM\r\n",
                             distanceCM);

                    Bluetooth_Send(message);
                }
            }
            else
            {
                if (obstacleDetected)
                {
                    obstacleDetected = 0;

                    Bluetooth_Send("OBSTACLE CLEARED\r\n");
                }
            }
        }

        /* ------------------------------------------------
           3. MOTOR CONTROL
           ------------------------------------------------ */

        Motor_Update();

        /* ------------------------------------------------
           4. EMERGENCY BUTTON
           ------------------------------------------------ */

        Button_Process();
    }
}

/* GPS FUNCTIONS -------------------------------------------------------------*/

static void GPS_StartReception(void)
{
    if (HAL_UART_Receive_IT(&huart1, &gpsRxByte, 1) != HAL_OK)
    {
        Error_Handler();
    }
}

/* GPS UART interrupt callback */

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1)
    {
        char received = (char)gpsRxByte;

        if (!gpsLineReady)
        {
            if (received == '\n')
            {
                gpsBuffer[gpsIndex] = '\0';

                gpsLineReady = 1;
            }
            else if (received != '\r')
            {
                if (gpsIndex < GPS_BUFFER_SIZE - 1)
                {
                    gpsBuffer[gpsIndex++] = received;
                }
                else
                {
                    gpsIndex = 0;
                }
            }
        }

        HAL_UART_Receive_IT(&huart1, &gpsRxByte, 1);
    }
}

/* Convert GPS coordinate to decimal degrees */

static float GPS_ConvertToDecimal(double coordinate, char direction)
{
    int degrees = (int)(coordinate / 100.0);

    double minutes = coordinate - (degrees * 100.0);

    float decimal = degrees + (minutes / 60.0);

    if (direction == 'S' || direction == 'W')
    {
        decimal = -decimal;
    }

    return decimal;
}

/* Parse GPS GGA sentence */

static void GPS_ProcessLine(char *line)
{
    char *gga = strstr(line, "GGA,");

    if (gga == NULL)
    {
        return;
    }

    gga += 4;

    double rawLatitude;
    double rawLongitude;

    char northSouth;
    char eastWest;

    int fixQuality;

    int result = sscanf(gga,
                        "%*[^,],%lf,%c,%lf,%c,%d",
                        &rawLatitude,
                        &northSouth,
                        &rawLongitude,
                        &eastWest,
                        &fixQuality);

    if (result == 5 && fixQuality > 0)
    {
        latitude = GPS_ConvertToDecimal(rawLatitude, northSouth);

        longitude = GPS_ConvertToDecimal(rawLongitude, eastWest);

        gpsFix = 1;
    }
    else
    {
        gpsFix = 0;
    }
}

/* ULTRASONIC SENSOR ---------------------------------------------------------*/

static float Ultrasonic_ReadDistance(void)
{
    uint32_t startTime;
    uint32_t timeout;

    uint16_t pulseStart;
    uint16_t pulseEnd;
    uint16_t pulseWidth;

    /* Trigger LOW */

    TRIG_LOW();

    /* Wait approximately 2 microseconds */

    startTime = __HAL_TIM_GET_COUNTER(&htim2);

    while ((uint16_t)(__HAL_TIM_GET_COUNTER(&htim2) -
                      startTime) < 2)
    {
    }

    /* Generate 10 microsecond pulse */

    TRIG_HIGH();

    startTime = __HAL_TIM_GET_COUNTER(&htim2);

    while ((uint16_t)(__HAL_TIM_GET_COUNTER(&htim2) -
                      startTime) < 10)
    {
    }

    TRIG_LOW();

    /* Wait for ECHO HIGH */

    timeout = HAL_GetTick();

    while (HAL_GPIO_ReadPin(ECHO_GPIO_Port,
                            ECHO_Pin) == GPIO_PIN_RESET)
    {
        if ((HAL_GetTick() - timeout) > ULTRASONIC_TIMEOUT_MS)
        {
            return -1.0f;
        }
    }

    /* Measure pulse width */

    pulseStart = (uint16_t)__HAL_TIM_GET_COUNTER(&htim2);

    while (HAL_GPIO_ReadPin(ECHO_GPIO_Port,
                            ECHO_Pin) == GPIO_PIN_SET)
    {
        if ((HAL_GetTick() - timeout) > ULTRASONIC_TIMEOUT_MS)
        {
            return -1.0f;
        }
    }

    pulseEnd = (uint16_t)__HAL_TIM_GET_COUNTER(&htim2);

    pulseWidth = (uint16_t)(pulseEnd - pulseStart);

    /* Convert microseconds to centimeters */

    return (float)pulseWidth / 58.0f;
}

/* MOTOR CONTROL -------------------------------------------------------------*/

static void Motor_Update(void)
{
    uint32_t currentTime = HAL_GetTick();

    if (obstacleDetected)
    {
        if (!motorState &&
            (currentTime - motorTimer >= MOTOR_OFF_TIME_MS))
        {
            MOTOR_ON();

            motorState = 1;

            motorTimer = currentTime;
        }

        if (motorState &&
            (currentTime - motorTimer >= MOTOR_ON_TIME_MS))
        {
            MOTOR_OFF();

            motorState = 0;

            motorTimer = currentTime;
        }
    }
    else
    {
        MOTOR_OFF();

        motorState = 0;

        motorTimer = currentTime;
    }
}

/* EMERGENCY BUTTON ----------------------------------------------------------*/

static void Button_Process(void)
{
    uint8_t reading =
        (uint8_t)HAL_GPIO_ReadPin(BUTTON_GPIO_Port, BUTTON_Pin);

    uint32_t currentTime = HAL_GetTick();

    if (reading != buttonLastReading)
    {
        buttonDebounceTimer = currentTime;

        buttonLastReading = reading;
    }

    if ((currentTime - buttonDebounceTimer) >= BUTTON_DEBOUNCE_MS)
    {
        if (reading != buttonStableState)
        {
            buttonStableState = reading;

            if (buttonStableState == GPIO_PIN_RESET)
            {
                Send_Emergency_Alert();
            }
        }
    }
}

/* BLUETOOTH FUNCTIONS -------------------------------------------------------*/

static void Bluetooth_Send(const char *message)
{
    HAL_UART_Transmit(&huart2,
                      (uint8_t *)message,
                      strlen(message),
                      500);
}

/* Send GPS location through Bluetooth */

static void Send_GPS_Location(const char *alert)
{
    char message[160];

    if (gpsFix)
    {
        snprintf(message,
                 sizeof(message),
                 "%s\r\nLatitude: %.6f\r\nLongitude: %.6f\r\n",
                 alert,
                 latitude,
                 longitude);
    }
    else
    {
        snprintf(message,
                 sizeof(message),
                 "%s\r\nGPS FIX NOT AVAILABLE\r\n",
                 alert);
    }

    Bluetooth_Send(message);
}

/* Emergency button alert */

static void Send_Emergency_Alert(void)
{
    MOTOR_ON();

    Send_GPS_Location("EMERGENCY BUTTON PRESSED!");

    HAL_Delay(200);

    MOTOR_OFF();
}

/* SYSTEM CLOCK CONFIGURATION -----------------------------------------------*/

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};

    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;

    RCC_OscInitStruct.HSEState = RCC_HSE_ON;

    RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;

    RCC_OscInitStruct.HSIState = RCC_HSI_ON;

    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;

    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;

    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    RCC_ClkInitStruct.ClockType =
        RCC_CLOCKTYPE_HCLK |
        RCC_CLOCKTYPE_SYSCLK |
        RCC_CLOCKTYPE_PCLK1 |
        RCC_CLOCKTYPE_PCLK2;

    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;

    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;

    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;

    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct,
                            FLASH_LATENCY_2) != HAL_OK)
    {
        Error_Handler();
    }
}

/* ERROR HANDLER -------------------------------------------------------------*/

void Error_Handler(void)
{
    __disable_irq();

    while (1)
    {
    }
}

#ifdef USE_FULL_ASSERT

void assert_failed(uint8_t *file, uint32_t line)
{
    /* User may add error reporting here */
}

#endif
