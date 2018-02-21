#ifdef STM32L1
	#include "stm32l1xx.h"
	#define LEDPORT (GPIOB)
	#define LED1 (6)
	#define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOBEN)
	#define _MODER    MODER
	#define GPIOMODER (GPIO_MODER_MODER6_0)
#elif STM32F1
	#include "stm32f1xx.h"
	#define LEDPORT (GPIOC)
	#define LED1 (13)
   #define ENABLE_GPIO_CLOCK (RCC->APB2ENR |= RCC_APB2ENR_IOPCEN)
   #define _MODER    CRH
   #define GPIOMODER (GPIO_CRH_MODE13_0)
#elif STM32F3
	#include "stm32f3xx.h"
	#define LEDPORT (GPIOE)
	#define LED1 (8)
	#define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOEEN)
	#define _MODER    MODER
	#define GPIOMODER (GPIO_MODER_MODER8_0)
#elif STM32F4
	#include "stm32f4xx.h"
	#define LEDPORT (GPIOD)
	#define LED1 (12)
	#define ENABLE_GPIO_CLOCK (RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN)
	#define _MODER    MODER
	#define GPIOMODER (GPIO_MODER_MODER12_0)
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
	ENABLE_GPIO_CLOCK; 		 					// enable the clock to GPIO
	LEDPORT->_MODER |= GPIOMODER;				// set pins to be general purpose output
	for (;;) {
		ms_delay(500);
		LEDPORT->ODR ^= (1<<LED1); 		// toggle diodes
	}
	
	return 0;
}