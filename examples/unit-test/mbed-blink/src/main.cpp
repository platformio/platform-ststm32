#include "mbed.h"

#ifndef UNIT_TEST

/*The leds are connected to different port pins on the
bluepill F103C8 and Disco F030R8 boards
*/

#ifdef STM32F1
DigitalOut myled(PC_13);
#endif
#ifdef STM32F0
DigitalOut myled(PC_9);
#endif

int main(void)
{
        while (1) {
                myled = 1;
                wait(1);
                myled = 0;
                wait(1);
        }
}
#endif
