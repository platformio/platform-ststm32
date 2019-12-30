#ifndef __SIMPLE_EEPROM__
#define __SIMPLE_EEPROM__

#ifdef __cplusplus
 extern "C" {
#endif

#include <stdint.h>

/*!
 * \brief Write to EEPROM memory
 */
void EEPROM_Write(uint32_t address, uint32_t value);


/*!
 * \brief Read from EEPROM memory
 */
uint32_t EEPROM_Read (uint32_t address);

#endif
