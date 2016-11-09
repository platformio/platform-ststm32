#include "mbed.h"

#ifndef UNIT_TEST
DigitalOut myled(PC_13);

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
