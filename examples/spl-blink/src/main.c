#ifdef STM32F1
	#include <stm32f10x_gpio.h>
	#include <stm32f10x_rcc.h>
	#if NUCLEO_F103RB
	/* default on-board LED */
	#define LEDPORT (GPIOA)
	#define LEDPIN (GPIO_Pin_5)
	#define ENABLE_GPIO_CLOCK (RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE))
	#else
	#define LEDPORT (GPIOC)
	#define LEDPIN (GPIO_Pin_13)
	#define ENABLE_GPIO_CLOCK (RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE))
	#endif
#elif STM32L1
	#include <stm32l1xx_gpio.h>
	#include <stm32l1xx_rcc.h>
	#define LEDPORT (GPIOB)
	#define LEDPIN (GPIO_Pin_7)
	#define ENABLE_GPIO_CLOCK (RCC_AHBPeriphClockCmd(RCC_AHBPeriph_GPIOB, ENABLE))
#elif STM32F3
	#include <stm32f30x_gpio.h>
	#include <stm32f30x_rcc.h>
	#define LEDPORT (GPIOE)
	#define LEDPIN (GPIO_Pin_8)
	#define ENABLE_GPIO_CLOCK (RCC_AHBPeriphClockCmd(RCC_AHBPeriph_GPIOE, ENABLE))
#elif STM32F4
	#include <stm32f4xx_gpio.h>
	#include <stm32f4xx_rcc.h>
	#define LEDPORT (GPIOD)
	#define LEDPIN (GPIO_Pin_12)
	#define ENABLE_GPIO_CLOCK (RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD, ENABLE))
#else
	#error "Please define one of the macros STM32F1, STM32L1, STM32F3 or STM32F4."
#endif

/* wanted blink time in milliseconds */
#define DELAY_TIME_MILLIS 1000

/* variable keeps track of timing delay */
static __IO uint32_t TimingDelay;

void Delay(__IO uint32_t nTime) {
	TimingDelay = nTime;
	/* wait until variable is decreased to 0 through ISR calls */
	while (TimingDelay != 0);
}

void TimingDelay_Decrement(void) {
	/* called in systick ISR */
	if (TimingDelay != 0x00) {
		TimingDelay--;
	}
}

/* system entry point */
int main(void)
{
	//setup SysTick for 1 millisecond interrupts
	if (SysTick_Config(SystemCoreClock / 1000)) {
		/* Capture error */
		while (1);
	}
	/* gpio init struct */
	GPIO_InitTypeDef gpio;
	/* enable clock GPIO */
	ENABLE_GPIO_CLOCK;
	/* use LED pin */
	gpio.GPIO_Pin = LEDPIN;
	gpio.GPIO_Speed = GPIO_Speed_2MHz;
	/* set pin to push-pull output depending on the SPL variant */
#if STM32F1
	gpio.GPIO_Mode = GPIO_Mode_Out_PP;
#else
	/* mode: output */
	gpio.GPIO_Mode = GPIO_Mode_OUT;
	/* output type: push-pull */
	gpio.GPIO_OType = GPIO_OType_PP;
#endif
	/* apply configuration */
	GPIO_Init(LEDPORT, &gpio);
	/* main program loop */
	for (;;) {
		/* set led on */
		GPIO_SetBits(LEDPORT, LEDPIN);
		/* delay */
		Delay(DELAY_TIME_MILLIS);
		/* clear led */
		GPIO_ResetBits(LEDPORT, LEDPIN);
		/* delay */
		Delay(DELAY_TIME_MILLIS);
	}

	/* never reached */
	return 0;
}

/* SysTick interrupt every millisecond */
void SysTick_Handler(void) {
	TimingDelay_Decrement();
}
