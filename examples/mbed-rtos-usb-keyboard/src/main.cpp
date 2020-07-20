/*
 * Copyright (c) 2006-2020 Arm Limited and affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */
#include "mbed.h"
#include "USBMouseKeyboard.h"

//LED1: NUM_LOCK
//LED2: CAPS_LOCK
//LED3: SCROLL_LOCK
BusOut leds(LED1, LED2, LED3);

//USBMouseKeyboard object
USBMouseKeyboard key_mouse;

int main(void)
{
    int16_t x = 0;
    int16_t y = 0;
    int32_t radius = 70;
    int32_t angle = 0;
    while (1) {
        //moves the coordinates of the mouse around in a circle
        x = cos((double)angle * 3.14 / 50.0) * radius;
        y = sin((double)angle * 3.14 / 50.0) * radius;
        //example of a media key press
        key_mouse.media_control(KEY_VOLUME_DOWN);
        //example of simple keyboard output
        key_mouse.printf("Hello World from Mbed\r\n");
        //function to move the mouse to coordinates "x, y"
        key_mouse.move(x, y);
        //example of modifier key press
        key_mouse.key_code(KEY_CAPS_LOCK);
        leds = key_mouse.lock_status();
        ThisThread::sleep_for(50);
        key_mouse.media_control(KEY_VOLUME_UP);
        key_mouse.key_code(KEY_NUM_LOCK);
        leds = key_mouse.lock_status();
        ThisThread::sleep_for(50);
        angle += 10;
        key_mouse.key_code(KEY_SCROLL_LOCK);
        leds = key_mouse.lock_status();
        ThisThread::sleep_for(50);
    }
}
