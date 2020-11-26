/**
  ******************************************************************************
  * @file    ExtMem_CodeExecution/ExtMem_Boot/Src/fmc.c
  * @author  MCD Application Team
  * @brief   This file includes the fmc-memories supported 
  *          STM32F723E-Discovery evaluation boards.
  @verbatim
  PartNumber supported by the file:
  -----------------------
   - IS61WV51216BLL-10M  : PSRAM external memory mounted on STM32F723E Discovery board.

  @endverbatim
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2016 STMicroelectronics International N.V. 
  * All rights reserved.</center></h2>
  *
  * Redistribution and use in source and binary forms, with or without 
  * modification, are permitted, provided that the following conditions are met:
  *
  * 1. Redistribution of source code must retain the above copyright notice, 
  *    this list of conditions and the following disclaimer.
  * 2. Redistributions in binary form must reproduce the above copyright notice,
  *    this list of conditions and the following disclaimer in the documentation
  *    and/or other materials provided with the distribution.
  * 3. Neither the name of STMicroelectronics nor the names of other 
  *    contributors to this software may be used to endorse or promote products 
  *    derived from this software without specific written permission.
  * 4. This software, including modifications and/or derivative works of this 
  *    software, must execute solely and exclusively on microcontroller or
  *    microprocessor devices manufactured by or for STMicroelectronics.
  * 5. Redistribution and use of this software other than as permitted under 
  *    this license is void and will automatically terminate your rights under 
  *    this license. 
  *
  * THIS SOFTWARE IS PROVIDED BY STMICROELECTRONICS AND CONTRIBUTORS "AS IS" 
  * AND ANY EXPRESS, IMPLIED OR STATUTORY WARRANTIES, INCLUDING, BUT NOT 
  * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
  * PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY INTELLECTUAL PROPERTY
  * RIGHTS ARE DISCLAIMED TO THE FULLEST EXTENT PERMITTED BY LAW. IN NO EVENT 
  * SHALL STMICROELECTRONICS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
  * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
  * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
  * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
  * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
  * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
  * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "stm32f7xx_hal.h"
#include "memory.h"
#include "memory_msp.h"

/** @addtogroup FMC
  * @{
  */ 
  
/** @defgroup FMC
  * @{
  */ 

/** @defgroup FMC_Private_Types_Definitions FMC Private Types Definitions
  * @{
  */ 
/**
  * @}
  */ 

/** @defgroup FMC_Private_Defines FMC Private Defines
  * @{
  */
/**
  * @}
  */ 

/** @defgroup FMC_Private_Macros FMC Private Macros
  * @{
  */  
/**
  * @}
  */ 

/** @defgroup FMC_Private_Variables FMC Private Variables
  * @{
  */       
/**
  * @}
  */ 
    
/** @defgroup FMC_Private_Functions FMC Private Functions
  * @{
  */

#if (DATA_AREA == USE_EXTERNAL_PSRAM) || (CODE_AREA == USE_EXTERNAL_PSRAM)
/** @defgroup PSRAM_Constants PSRAM Defines
  * @{
  */
/* #define PSRAM_MEMORY_WIDTH    FMC_NORSRAM_MEM_BUS_WIDTH_8*/
#define PSRAM_MEMORY_WIDTH    FMC_NORSRAM_MEM_BUS_WIDTH_16

#define PSRAM_BURSTACCESS     FMC_BURST_ACCESS_MODE_DISABLE
/* #define PSRAM_BURSTACCESS     FMC_BURST_ACCESS_MODE_ENABLE*/
  
#define PSRAM_WRITEBURST      FMC_WRITE_BURST_DISABLE
/* #define PSRAM_WRITEBURST     FMC_WRITE_BURST_ENABLE */
 
#define PSRAM_CONTINUOUSCLOCK    FMC_CONTINUOUS_CLOCK_SYNC_ONLY 
/* #define PSRAM_CONTINUOUSCLOCK     FMC_CONTINUOUS_CLOCK_SYNC_ASYNC */  
/**
  * @}
  */
/**
  * @brief  Initializes the PSRAM device.
  * @retval PSRAM status
  */
uint32_t PSRAM_Startup(void)
{
  static FMC_NORSRAM_TimingTypeDef Timing;  
  SRAM_HandleTypeDef psramHandle;
  
  /* PSRAM device configuration */
  psramHandle.Instance = FMC_NORSRAM_DEVICE;
  psramHandle.Extended = FMC_NORSRAM_EXTENDED_DEVICE;
  
  /* PSRAM device configuration */
  /* Timing configuration derived from system clock (up to 216Mhz)
     for 108Mhz as PSRAM clock frequency */
  Timing.AddressSetupTime      = 9;
  Timing.AddressHoldTime       = 2;
  Timing.DataSetupTime         = 6;
  Timing.BusTurnAroundDuration = 1;
  Timing.CLKDivision           = 2;
  Timing.DataLatency           = 2;
  Timing.AccessMode            = FMC_ACCESS_MODE_A;
  
  psramHandle.Init.NSBank             = FMC_NORSRAM_BANK1;
  psramHandle.Init.DataAddressMux     = FMC_DATA_ADDRESS_MUX_DISABLE;
  psramHandle.Init.MemoryType         = FMC_MEMORY_TYPE_SRAM;
  psramHandle.Init.MemoryDataWidth    = PSRAM_MEMORY_WIDTH;
  psramHandle.Init.BurstAccessMode    = PSRAM_BURSTACCESS;
  psramHandle.Init.WaitSignalPolarity = FMC_WAIT_SIGNAL_POLARITY_LOW;
  psramHandle.Init.WaitSignalActive   = FMC_WAIT_TIMING_BEFORE_WS;
  psramHandle.Init.WriteOperation     = FMC_WRITE_OPERATION_ENABLE;
  psramHandle.Init.WaitSignal         = FMC_WAIT_SIGNAL_DISABLE;
  psramHandle.Init.ExtendedMode       = FMC_EXTENDED_MODE_DISABLE;
  psramHandle.Init.AsynchronousWait   = FMC_ASYNCHRONOUS_WAIT_DISABLE;
  psramHandle.Init.WriteBurst         = PSRAM_WRITEBURST;
  psramHandle.Init.WriteFifo          = FMC_WRITE_FIFO_DISABLE;
  psramHandle.Init.PageSize           = FMC_PAGE_SIZE_NONE;  
  psramHandle.Init.ContinuousClock    = PSRAM_CONTINUOUSCLOCK;
  
  /* PSRAM controller initialization */
  PSRAM_MspInit();
  if (HAL_SRAM_Init(&psramHandle, &Timing, &Timing) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  return MEMORY_OK;
}
#endif /*(DATA_AREA == USE_EXTERNAL_PSRAM) || (CODE_AREA == USE_EXTERNAL_PSRAM)*/

/**
  * @}
  */  
  
/**
  * @}
  */ 
  
/**
  * @}
  */
/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
