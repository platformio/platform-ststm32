#ifdef STM32L0
    #include "stm32l0xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (3)
    #define ENABLE_GPIO_CLOCK (RCC->IOPENR |= RCC_IOPENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODE3_0)
#elif STM32L1
    #include "stm32l1xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (6)
    #define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER6_0)
#elif STM32L4
    #include "stm32l4xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (3)
    #define ENABLE_GPIO_CLOCK (RCC->AHB2ENR |= RCC_AHB2ENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODE3_0)
#elif STM32L5
    #include "stm32l5xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (6)
    #define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER6_0)
#elif STM32F0
    #include "stm32f0xx.h"
    #define LEDPORT (GPIOC)
    #define LED1 (8)
    #define ENABLE_GPIO_CLOCK (RCC->APB2ENR |= RCC_AHBENR_GPIOCEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER8_0)
#elif STM32F1
    #include "stm32f1xx.h"
    #define LEDPORT (GPIOC)
    #define LED1 (13)
    #define ENABLE_GPIO_CLOCK (RCC->APB2ENR |= RCC_APB2ENR_IOPCEN)
    #define _MODER    CRH
    #define GPIOMODER (GPIO_CRH_MODE13_0)
#elif STM32F2
    #include "stm32f2xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (0)
    #define ENABLE_GPIO_CLOCK (RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER8_0)
#elif STM32F3
    #include "stm32f3xx.h"
    #define LEDPORT (GPIOE)
    #define LED1 (8)
    #define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOAEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER8_0)
#elif STM32F4
    #include "stm32f4xx.h"
    #define LEDPORT (GPIOD)
    #define LED1 (12)
    #define ENABLE_GPIO_CLOCK (RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER12_0)
#elif STM32F7
    #include "stm32f7xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (0)
    #define ENABLE_GPIO_CLOCK (RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODER0_0)
#elif STM32H7
    #include "stm32h7xx.h"
    #define LEDPORT (GPIOB)
    #define LED1 (0)
    #define ENABLE_GPIO_CLOCK (RCC->AHB4ENR |= RCC_AHB4ENR_GPIOBEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODE0_0)
#elif STM32G0
    #include "stm32g0xx.h"
    #define LEDPORT (GPIOA)
    #define LED1 (5)
    #define ENABLE_GPIO_CLOCK (RCC->IOPENR |= RCC_IOPENR_GPIOAEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODE5_0)
#elif STM32G4
    #include "stm32g4xx.h"
    #define LEDPORT (GPIOA)
    #define LED1 (5)
    #define ENABLE_GPIO_CLOCK (RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN)
    #define _MODER    MODER
    #define GPIOMODER (GPIO_MODER_MODE5_0)
#endif


void ms_delay(int ms)
{
   while (ms-- > 0) {
      volatile int x=500;
      while (x-- > 0)
         __asm("nop");
   }
}

//Alternates blue and green LEDs quickly
int main(void)
{
    ENABLE_GPIO_CLOCK;              // enable the clock to GPIO
    LEDPORT->_MODER |= GPIOMODER;   // set pins to be general purpose output
    for (;;) {
    ms_delay(500);
    LEDPORT->ODR ^= (1<<LED1);  // toggle diodes
    }

    return 0;
}
