/**
  ******************************************************************************
  * @file    ExtMem_CodeExecution/ExtMem_Boot/Src/qspi.c
  * @author  MCD Application Team
  * @brief   This file includes a driver for QSPI flashes support mounted on
  *          STM32F723E-Discovery evaluation boards.
  @verbatim
  PartNumber supported by the file:
  -----------------------
   - MX25L512    :  QSPI Flash memory mounted on STM32F723E Discovery board.
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
#include "mx25l512.h"

/** @addtogroup QSPI
  * @{
  */ 
  
/** @defgroup QSPI
  * @{
  */ 


/* Private variables ---------------------------------------------------------*/

/** @defgroup QSPI_Private_Variables QSPI Private Variables
  * @{
  */       
QSPI_HandleTypeDef       QSPIHandle;
QSPI_CommandTypeDef      sCommand;
QSPI_AutoPollingTypeDef  sConfig;
/**
  * @}
  */ 

/* Private Macros ------------------------------------------------------------*/
/* Private functions ---------------------------------------------------------*/
    
/** @defgroup QSPI_Private_Functions QSPI Private Functions
  * @{
  */ 
static uint32_t QSPI_ResetMemory(QSPI_HandleTypeDef *hqspi);
static uint32_t QSPI_EnterFourBytesAddress(QSPI_HandleTypeDef *hqspi);
static uint32_t QSPI_DummyCyclesCfg(QSPI_HandleTypeDef *hqspi);
static uint32_t QSPI_EnterMemory_QPI(QSPI_HandleTypeDef *hqspi);
static uint32_t QSPI_OutDrvStrengthCfg(QSPI_HandleTypeDef *hqspi);
static uint32_t QSPI_WriteEnable(QSPI_HandleTypeDef *hqspi);
static uint32_t QSPI_AutoPollingMemReady(QSPI_HandleTypeDef *hqspi, uint32_t Timeout);
static uint32_t QSPI_EnableMemoryMappedMode(QSPI_HandleTypeDef *hqspi);

/**
  * @}
  */
    
/** @defgroup QSPI_Exported_Functions QSPI Exported Functions
  * @{
  */ 

/**
  * @brief  Initializes and configure the QSPI interface.
  * @retval QSPI memory status
  */
uint32_t QSPI_Startup(uint32_t Mode)
{ 
  QSPIHandle.Instance = QUADSPI;
  
  /* Call the DeInit function to reset the driver */
  if (HAL_QSPI_DeInit(&QSPIHandle) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* System level initialization */
  QSPI_MspInit();

  /* sCommand initialize common parameter */
  sCommand.AddressMode       = QSPI_ADDRESS_NONE;
  sCommand.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
  sCommand.DataMode          = QSPI_DATA_NONE;
  sCommand.DummyCycles       = 0;
  sCommand.DdrMode           = QSPI_DDR_MODE_DISABLE;
  sCommand.DdrHoldHalfCycle  = QSPI_DDR_HHC_ANALOG_DELAY;
  sCommand.SIOOMode          = QSPI_SIOO_INST_EVERY_CMD;
  sCommand.AddressSize       = QSPI_ADDRESS_32_BITS;
  
  /* sConfig initialize common parameter */
  sConfig.MatchMode       = QSPI_MATCH_MODE_AND;
  sConfig.StatusBytesSize = 1;
  sConfig.Interval        = 0x10;
  sConfig.AutomaticStop   = QSPI_AUTOMATIC_STOP_ENABLE;

  /* QSPI initialization */
  /* QSPI freq = SYSCLK /(1 + ClockPrescaler) = 200 MHz/(1+1) = 100 Mhz */
  QSPIHandle.Init.ClockPrescaler     = 1;   /* QSPI freq = 200 MHz/(1+1) = 100 Mhz */
  QSPIHandle.Init.FifoThreshold      = 16;
  QSPIHandle.Init.SampleShifting     = QSPI_SAMPLE_SHIFTING_HALFCYCLE; 
  QSPIHandle.Init.FlashSize          = POSITION_VAL(MX25L512_FLASH_SIZE) - 1;
  QSPIHandle.Init.ChipSelectHighTime = QSPI_CS_HIGH_TIME_4_CYCLE; /* Min 30ns for nonRead */
  QSPIHandle.Init.ClockMode          = QSPI_CLOCK_MODE_0;
  QSPIHandle.Init.FlashID            = QSPI_FLASH_ID_1;
  QSPIHandle.Init.DualFlash          = QSPI_DUALFLASH_DISABLE;
  
  if (HAL_QSPI_Init(&QSPIHandle) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* QSPI memory reset */
  if (QSPI_ResetMemory(&QSPIHandle))
  {
    return MEMORY_ERROR;
  }
  
  /* Put QSPI memory in QPI mode */
  if( QSPI_EnterMemory_QPI( &QSPIHandle )!=MEMORY_OK )
  {
    return MEMORY_ERROR;
  }
  
  /* Set the QSPI memory in 4-bytes address mode */
  if (QSPI_EnterFourBytesAddress(&QSPIHandle) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Configuration of the dummy cycles on QSPI memory side */
  if (QSPI_DummyCyclesCfg(&QSPIHandle) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Configuration of the Output driver strength on memory side */
  if( QSPI_OutDrvStrengthCfg( &QSPIHandle ) != MEMORY_OK )
  {
    return MEMORY_ERROR;
  }
  
  /* Enable MemoryMapped mode */
  if( QSPI_EnableMemoryMappedMode( &QSPIHandle ) != MEMORY_OK )
  {
    return MEMORY_ERROR;
  }

  return MEMORY_OK;
}


/**
  * @}
  */

/** @addtogroup QSPI_Private_Functions
  * @{
  */ 


/**
  * @brief  Configure the QSPI in memory-mapped mode
  * @retval QSPI memory status
  */
static uint32_t QSPI_EnableMemoryMappedMode(QSPI_HandleTypeDef *hqspi)
{
  QSPI_MemoryMappedTypeDef s_mem_mapped_cfg;

  /* Configure the command for the read instruction */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.Instruction       = QSPI_READ_4_BYTE_ADDR_CMD;
  sCommand.AddressMode       = QSPI_ADDRESS_4_LINES;
  sCommand.DataMode          = QSPI_DATA_4_LINES;
  sCommand.DummyCycles       = MX25L512_DUMMY_CYCLES_READ_QUAD_IO;
  
  /* Configure the memory mapped mode */
  s_mem_mapped_cfg.TimeOutActivation = QSPI_TIMEOUT_COUNTER_DISABLE;
  s_mem_mapped_cfg.TimeOutPeriod     = 0;
  
  if (HAL_QSPI_MemoryMapped(hqspi, &sCommand, &s_mem_mapped_cfg) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  return MEMORY_OK;
}

/**
  * @brief  This function reset the QSPI memory.
  * @param  hqspi: QSPI handle
  * @retval None
  */
static uint32_t QSPI_ResetMemory(QSPI_HandleTypeDef *hqspi)
{
  uint8_t                  reg;

  /* Send command RESET command in QPI mode (QUAD I/Os) */
  /* Initialize the reset enable command */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.Instruction       = RESET_ENABLE_CMD;
  sCommand.DataMode          = QSPI_DATA_NONE;

  /* Send the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  /* Send the reset memory command */
  sCommand.Instruction = RESET_MEMORY_CMD;
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }  

  /* Send command RESET command in SPI mode */
  /* Initialize the reset enable command */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
  sCommand.Instruction       = RESET_ENABLE_CMD;
  /* Send the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Send the reset memory command */
  sCommand.Instruction = RESET_MEMORY_CMD;
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* After reset CMD, 1000ms requested if QSPI memory SWReset occured during full chip erase operation */
  HAL_Delay( 1000 );

  /* Configure automatic polling mode to wait the memory is ready */  
  if (QSPI_AutoPollingMemReady(hqspi, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }

  /* Initialize the reading of status register */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
  sCommand.Instruction       = READ_STATUS_REG_CMD;
  sCommand.DataMode          = QSPI_DATA_1_LINE;
  sCommand.NbData            = 1;

  /* Configure the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Reception of the data */
  if (HAL_QSPI_Receive(hqspi, &reg, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Enable write operations, command in 1 bit */
  /* Enable write operations */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
  sCommand.Instruction       = WRITE_ENABLE_CMD;
  sCommand.DataMode          = QSPI_DATA_NONE;

  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Configure automatic polling mode to wait for write enabling */  
  sConfig.Match           = MX25L512_SR_WREN;
  sConfig.Mask            = MX25L512_SR_WREN;

  sCommand.Instruction    = READ_STATUS_REG_CMD;
  sCommand.DataMode       = QSPI_DATA_1_LINE;

  if (HAL_QSPI_AutoPolling(hqspi, &sCommand, &sConfig, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Update the configuration register with new dummy cycles */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
  sCommand.Instruction       = WRITE_STATUS_CFG_REG_CMD;
  sCommand.NbData            = 1;

  /* Enable the Quad IO on the QSPI memory (Non-volatile bit) */
  reg |= MX25L512_SR_QUADEN;

  /* Configure the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Transmission of the data */
  if (HAL_QSPI_Transmit(hqspi, &reg, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* 40ms  Write Status/Configuration Register Cycle Time */
  HAL_Delay( 40 );  

  return MEMORY_OK;
}

/**
  * @brief  This function set the QSPI memory in 4-byte address mode
  * @param  hqspi: QSPI handle
  * @retval None
  */
static uint32_t QSPI_EnterFourBytesAddress(QSPI_HandleTypeDef *hqspi)
{
  /* Initialize the command */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.Instruction       = ENTER_4_BYTE_ADDR_MODE_CMD;
  sCommand.DataMode          = QSPI_DATA_NONE;

  /* Enable write operations */
  if (QSPI_WriteEnable(hqspi) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }

  /* Send the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Configure automatic polling mode to wait the memory is ready */  
  if (QSPI_AutoPollingMemReady(hqspi, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }

  return MEMORY_OK;
}

/**
  * @brief  This function configure the dummy cycles on memory side.
  * @param  hqspi: QSPI handle
  * @retval None
  */
static uint32_t QSPI_DummyCyclesCfg(QSPI_HandleTypeDef *hqspi)
{
  uint8_t reg[2];
  
  /* Initialize the reading of status register */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.DataMode          = QSPI_DATA_4_LINES;
  
  sCommand.NbData            = 1;
  sCommand.Instruction       = READ_STATUS_REG_CMD;

  /* Configure the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Reception of the data */
  if (HAL_QSPI_Receive(hqspi, &(reg[0]), HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Initialize the reading of configuration register */
  sCommand.Instruction       = READ_CFG_REG_CMD;
  sCommand.NbData            = 1;
  
  /* Configure the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Reception of the data */
  if (HAL_QSPI_Receive(hqspi, &(reg[1]), HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Enable write operations */
  if (QSPI_WriteEnable(hqspi) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Update the configuration register with new dummy cycles */
  sCommand.Instruction       = WRITE_STATUS_CFG_REG_CMD;
  sCommand.NbData            = 2;
  
  /* MX25L512_DUMMY_CYCLES_READ_QUAD = 3 for 10 cycles in QPI mode */
  MODIFY_REG( reg[1], MX25L512_CR_NB_DUMMY, (MX25L512_DUMMY_CYCLES_READ_QUAD << POSITION_VAL(MX25L512_CR_NB_DUMMY)));
  
  /* Configure the write volatile configuration register command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Transmission of the data */
  if (HAL_QSPI_Transmit(hqspi, &(reg[0]), HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* 40ms  Write Status/Configuration Register Cycle Time */
  HAL_Delay( 40 );  
  
  return MEMORY_OK;
}

/**
  * @brief  This function put QSPI memory in QPI mode (quad I/O).
  * @param  hqspi: QSPI handle
  * @retval None
  */
static uint32_t QSPI_EnterMemory_QPI( QSPI_HandleTypeDef *hqspi )
{
  /* Initialize the QPI enable command */
  /* QSPI memory is supported to be in SPI mode, so CMD on 1 LINE */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_1_LINE;  
  sCommand.Instruction       = ENTER_QUAD_CMD;
  sCommand.DataMode          = QSPI_DATA_NONE;

  /* Send the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Configure automatic polling mode to wait the QUADEN bit=1 and WIP bit=0 */
  sConfig.Match           = MX25L512_SR_QUADEN;
  sConfig.Mask            = MX25L512_SR_QUADEN|MX25L512_SR_WIP;

  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.Instruction       = READ_STATUS_REG_CMD;
  sCommand.DataMode          = QSPI_DATA_4_LINES;

  if (HAL_QSPI_AutoPolling(hqspi, &sCommand, &sConfig, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  return MEMORY_OK;
}

/**
  * @brief  This function configure the Output driver strength on memory side.
  * @param  hqspi: QSPI handle
  * @retval None
  */
static uint32_t QSPI_OutDrvStrengthCfg( QSPI_HandleTypeDef *hqspi )
{
  uint8_t reg[2];

  /* Initialize the reading of status register */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.DataMode          = QSPI_DATA_4_LINES;

  sCommand.Instruction       = READ_STATUS_REG_CMD;
  sCommand.NbData            = 1;

  /* Configure the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Reception of the data */
  if (HAL_QSPI_Receive(hqspi, &(reg[0]), HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Initialize the reading of configuration register */
  sCommand.Instruction       = READ_CFG_REG_CMD;
  sCommand.NbData            = 1;

  /* Configure the command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Reception of the data */
  if (HAL_QSPI_Receive(hqspi, &(reg[1]), HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Enable write operations */
  if (QSPI_WriteEnable(&QSPIHandle) != MEMORY_OK)
  {
    return MEMORY_ERROR;
  }

  /* Update the configuration register with new output driver strength */
  sCommand.Instruction       = WRITE_STATUS_CFG_REG_CMD;
  sCommand.NbData            = 2;

  /* Set Output Strength of the QSPI memory 15 ohms */
  MODIFY_REG( reg[1], MX25L512_CR_ODS, (MX25L512_CR_ODS_15 << POSITION_VAL(MX25L512_CR_ODS)));

  /* Configure the write volatile configuration register command */
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  /* Transmission of the data */
  if (HAL_QSPI_Transmit(hqspi, &(reg[0]), HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  return MEMORY_OK;
}

/**
  * @brief  This function send a Write Enable and wait it is effective.
  * @param  hqspi: QSPI handle
  * @retval None
  */
static uint32_t QSPI_WriteEnable(QSPI_HandleTypeDef *hqspi)
{
  /* Enable write operations */
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.Instruction       = WRITE_ENABLE_CMD;
  sCommand.DataMode          = QSPI_DATA_NONE;
  
  if (HAL_QSPI_Command(hqspi, &sCommand, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  /* Configure automatic polling mode to wait for write enabling */  
  sConfig.Match           = MX25L512_SR_WREN;
  sConfig.Mask            = MX25L512_SR_WREN;
  
  sCommand.Instruction    = READ_STATUS_REG_CMD;
  sCommand.DataMode       = QSPI_DATA_4_LINES;
  
  if (HAL_QSPI_AutoPolling(hqspi, &sCommand, &sConfig, HAL_QPSI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
  {
    return MEMORY_ERROR;
  }
  
  return MEMORY_OK;
}

/**
  * @brief  This function read the SR of the memory and wait the EOP.
  * @param  hqspi: QSPI handle
  * @param  Timeout
  * @retval None
  */
static uint32_t QSPI_AutoPollingMemReady(QSPI_HandleTypeDef *hqspi, uint32_t Timeout)
{
  /* Configure automatic polling mode to wait for memory ready */  
  sCommand.InstructionMode   = QSPI_INSTRUCTION_4_LINES;
  sCommand.Instruction       = READ_STATUS_REG_CMD;
  sCommand.DataMode          = QSPI_DATA_4_LINES;

  sConfig.Match           = 0;
  sConfig.Mask            = MX25L512_SR_WIP;

  if (HAL_QSPI_AutoPolling(hqspi, &sCommand, &sConfig, Timeout) != HAL_OK)
  {
    return MEMORY_ERROR;
  }

  return MEMORY_OK;
}
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
