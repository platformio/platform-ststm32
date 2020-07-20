/*
 * Copyright (c) 2020 Arm Limited and affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */
#include "mbed.h"

// Creates an event bound to the specified event queue
EventQueue queue;
void handler(int count);
Event<void(int)> event(&queue, handler);

void handler(int count)
{
    printf("Event = %d \n", count);
    return;
}

void post_events(void)
{

    // Events can be posted multiple times and enqueue gracefully until
    // the dispatch function is called.
    event.post(1);
    event.post(2);
    event.post(3);
}

int main()
{

    Thread event_thread;

    // The event can be manually configured for special timing requirements
    // specified in milliseconds
    event.delay(100);       // Starting delay - 100 msec
    event.period(200);      // Delay between each evet - 200msec

    event_thread.start(callback(post_events));

    // Posted events are dispatched in the context of the queue's
    // dispatch function
    queue.dispatch(400);        // Dispatch time - 400msec
    // 400 msec - Only 2 set of events will be dispatched as period is 200 msec

    event_thread.join();
}


