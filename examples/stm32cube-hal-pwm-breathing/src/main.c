/*
 * STM32Cube HAL - PWM Breathing LED Example
 *
 * This example demonstrates a smooth "breathing" LED effect using PWM.
 * It is compatible with STM32F0 series boards.
 *
 * Supported Boards:
 * - Nucleo-F030R8
 * - Nucleo-F070RB
 * - Nucleo-F072RB
 * - Nucleo-F091RC
 *
 * Hardware Setup:
 * - PA5: Connect the onboard LED pin in analog mode.
 * - PA6: PWM output using TIM3 Channel 1.
 * - Jumper wire from PA6 to PA5.
 *
 * Author: Kiran Jojare
 */

#if F0
#include "stm32f0xx_hal.h"
#else
#error "Unsupported STM32 Family"
#endif

#include <math.h>

// LED GPIO Pin and Timer Definitions
#define LED_PIN                                GPIO_PIN_5
#define LED_GPIO_PORT                          GPIOA
#define LED_GPIO_CLK_ENABLE()                  __HAL_RCC_GPIOA_CLK_ENABLE()
#define PWM_PIN                                GPIO_PIN_6
#define PWM_GPIO_PORT                          GPIOA
#define PWM_GPIO_CLK_ENABLE()                  __HAL_RCC_GPIOA_CLK_ENABLE()
#define PWM_GPIO_AF                            GPIO_AF1_TIM3
#define PWM_TIMER                              TIM3
#define PWM_CHANNEL                            TIM_CHANNEL_1

// Function Prototypes
void SystemClock_Config(void);
void Error_Handler(void);
static void MX_GPIO_Init(void);
static void MX_TIM3_Init(void);

// Timer Handle
TIM_HandleTypeDef htim3;

int main(void)
{
    // HAL Initialization
    HAL_Init();

    // Configure System Clock
    SystemClock_Config();

    // Initialize GPIO and Timer
    MX_GPIO_Init();
    MX_TIM3_Init();

    // Start PWM Output
    if (HAL_TIM_PWM_Start(&htim3, PWM_CHANNEL) != HAL_OK)
    {
        Error_Handler();
    }

    // Variables for Breathing Effect
    float phase = 0.0f; // Phase of the sine wave
    uint32_t duty_cycle;

    while (1)
    {
        // Calculate Duty Cycle with Sinusoidal Variation
        duty_cycle = (uint32_t)((sinf(phase) + 1.0f) * 500); // Scale to 0-1000 range
        __HAL_TIM_SET_COMPARE(&htim3, PWM_CHANNEL, duty_cycle);

        // Increment Phase
        phase += 0.05f; // Adjust for breathing speed
        if (phase >= 2 * M_PI)
        {
            phase -= 2 * M_PI;
        }

        HAL_Delay(10); // Smooth breathing effect
    }
}

// System Clock Configuration
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    // Configure the main internal regulator output voltage
    HAL_PWR_EnableBkUpAccess();

    // Initializes the RCC Oscillators
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI; // Use HSI as PLL source
    RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV1;      // Prescaler
    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;        // PLL Multiplier for 48 MHz
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    // Initializes the CPU, AHB, and APB buses clocks
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK; // Use PLL as system clock source
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;        // AHB Prescaler
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;         // APB1 Prescaler

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
    {
        Error_Handler();
    }
}


// GPIO Initialization
static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // Enable GPIOA Clock
    LED_GPIO_CLK_ENABLE();
    PWM_GPIO_CLK_ENABLE();

    // Configure LED Pin (PA5) in Analog Mode
    GPIO_InitStruct.Pin = LED_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(LED_GPIO_PORT, &GPIO_InitStruct);

    // Configure PWM Pin (PA6) for Alternate Function
    GPIO_InitStruct.Pin = PWM_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    GPIO_InitStruct.Alternate = PWM_GPIO_AF;
    HAL_GPIO_Init(PWM_GPIO_PORT, &GPIO_InitStruct);
}

// Timer 3 Initialization for PWM
static void MX_TIM3_Init(void)
{
    TIM_OC_InitTypeDef sConfigOC = {0};

    __HAL_RCC_TIM3_CLK_ENABLE();

    htim3.Instance = PWM_TIMER;
    htim3.Init.Prescaler = 48 - 1; // 1 MHz Timer Clock
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 1000 - 1; // 1 kHz PWM Frequency
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;

    if (HAL_TIM_PWM_Init(&htim3) != HAL_OK)
    {
        Error_Handler();
    }

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 0;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;

    if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, PWM_CHANNEL) != HAL_OK)
    {
        Error_Handler();
    }
}

// Error Handler
void Error_Handler(void)
{
    while (1)
    {
    }
}
