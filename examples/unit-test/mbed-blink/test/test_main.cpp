#include "mbed.h"
#include "unity.h"

#ifdef UNIT_TEST

#ifdef STM32F1
DigitalOut myled(PC_13);
#endif
#ifdef STM32F0
DigitalOut myled(PC_9);
#endif


void test_led_write_high(void)
{
        myled.write(1);
        TEST_ASSERT_EQUAL(myled.read(), 1);
}

void test_led_write_low(void)
{
        myled.write(0);
        TEST_ASSERT_EQUAL(myled.read(), 0);
}

int main(void)
{
        UNITY_BEGIN();

        wait(1);
// Without the above delay, the console does not print the PASS/FAIL message
// for the first couple of unit tests
        RUN_TEST(test_led_write_high);
        wait(0.5);
        RUN_TEST(test_led_write_low);
        wait(0.5);
        UNITY_END();
}


#endif
