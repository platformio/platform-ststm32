#ifndef STM32F1
#error "This example is for an STM32F1 series board!"
#endif
#include <stm32f10x.h>
#include <stm32f10x_gpio.h>
#include <stm32f10x_rcc.h>

/* blinky for PC_13 (on-board red LED) */
#define LEDPORT (GPIOC)
#define LEDPIN (GPIO_Pin_13)
#define ENABLE_GPIO_CLOCK (RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE))
/* toggle time */
#define DELAY_TIME_MILLIS 1000

/* variable keeps track of timing delay */
static __IO uint32_t TimingDelay;

/**
  * @brief  Inserts a delay time.
  * @param  nTime: specifies the delay time length, in milliseconds.
  * @retval None
  */
void Delay(__IO uint32_t nTime)
{
  TimingDelay = nTime;

  while(TimingDelay != 0);
}

void TimingDelay_Decrement(void)
{
  if (TimingDelay != 0x00)
  {
    TimingDelay--;
  }
}

/* system entry point */
int main(void)
{
	//setup SysTick for 1 millisecond interrupts
	if (SysTick_Config(SystemCoreClock / 1000))
	{
		/* Capture error */
		while (1);
	}
	/* gpio init struct */
	GPIO_InitTypeDef gpio;
	/* enable clock GPIO */
	ENABLE_GPIO_CLOCK;
	/* use LED pin */
	gpio.GPIO_Pin = LEDPIN;
	/* mode: output */
	gpio.GPIO_Mode = GPIO_Mode_Out_PP;
	gpio.GPIO_Speed = GPIO_Speed_50MHz;
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

/******************************************************************************/
/*            Cortex-M3 Processor Exceptions Handlers                         */
/******************************************************************************/

void NMI_Handler(void)
{
}

void HardFault_Handler(void)
{
  /* Go to infinite loop when Hard Fault exception occurs */
  while (1)
  {
  }
}

void MemManage_Handler(void)
{
  /* Go to infinite loop when Memory Manage exception occurs */
  while (1)
  {
  }
}

void BusFault_Handler(void)
{
  /* Go to infinite loop when Bus Fault exception occurs */
  while (1)
  {
  }
}

void UsageFault_Handler(void)
{
  /* Go to infinite loop when Usage Fault exception occurs */
  while (1)
  {
  }
}

void SVC_Handler(void)
{
}

void DebugMon_Handler(void)
{
}

void PendSV_Handler(void)
{
}

void SysTick_Handler(void)
{
	//decrement timing delay here
	TimingDelay_Decrement();
}