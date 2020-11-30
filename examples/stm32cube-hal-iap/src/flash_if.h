/**
  ******************************************************************************
  * @file    IAP_Main/Inc/flash_if.h 
  * @author  MCD Application Team
  * @brief   This file provides all the headers of the flash_if functions.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2016 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under Ultimate Liberty license
  * SLA0044, the "License"; You may not use this file except in compliance with
  * the License. You may obtain a copy of the License at:
  *                             www.st.com/SLA0044
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __FLASH_IF_H
#define __FLASH_IF_H

/* Includes ------------------------------------------------------------------*/
#include "stm32f3xx_hal.h"

/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/


/* Error code */
enum 
{
  FLASHIF_OK = 0,
  FLASHIF_ERASEKO,
  FLASHIF_WRITINGCTRL_ERROR,
  FLASHIF_WRITING_ERROR,
  FLASHIF_PROTECTION_ERRROR
};

/* protection type */  
enum{
  FLASHIF_PROTECTION_NONE         = 0,
  FLASHIF_PROTECTION_PCROPENABLED = 0x1,
  FLASHIF_PROTECTION_WRPENABLED   = 0x2,
  FLASHIF_PROTECTION_RDPENABLED   = 0x4,
};

/* protection update */
enum {
	FLASHIF_WRP_ENABLE,
	FLASHIF_WRP_DISABLE
};

/* Define the address from where user application will be loaded.
   Note: this area is reserved for the IAP code                  */
#define FLASH_PAGE_STEP         FLASH_PAGE_SIZE           /* Size of page : 2 Kbytes */
#define APPLICATION_ADDRESS     (uint32_t)0x08004000      /* Start user code address: ADDR_FLASH_PAGE_8 */

/* Notable Flash addresses */
#define FLASH_START		              ((uint32_t)0x08000000)
#define USER_FLASH_END_ADDRESS        0x08040000

/* Define the user application size */
#define USER_FLASH_SIZE               ((uint32_t)0x00003000) /* Small default template application */

/* Define bitmap representing user flash area that could be write protected (check restricted to pages 8-39). */
#define FLASH_PAGE_TO_BE_PROTECTED (OB_WRP_PAGES8TO9 | OB_WRP_PAGES10TO11 | OB_WRP_PAGES12TO13 | OB_WRP_PAGES14TO15 | \
                                    OB_WRP_PAGES16TO17 | OB_WRP_PAGES18TO19 | OB_WRP_PAGES20TO21 | OB_WRP_PAGES22TO23 | \
                                    OB_WRP_PAGES24TO25 | OB_WRP_PAGES26TO27 | OB_WRP_PAGES28TO29 | OB_WRP_PAGES30TO31 | \
                                    OB_WRP_PAGES32TO33 | OB_WRP_PAGES34TO35 | OB_WRP_PAGES36TO37 | OB_WRP_PAGES38TO39  )  


/* Exported macro ------------------------------------------------------------*/
/* ABSoulute value */
#define ABS_RETURN(x,y)               (((x) < (y)) ? (y) : (x))

/* Exported functions ------------------------------------------------------- */
void FLASH_If_Init(void);
uint32_t FLASH_If_Erase(uint32_t StartSector);
uint32_t FLASH_If_GetWriteProtectionStatus(void);
uint32_t FLASH_If_Write(uint32_t destination, uint32_t *p_source, uint32_t length);
uint32_t FLASH_If_WriteProtectionConfig(uint32_t protectionstate);

#endif  /* __FLASH_IF_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
