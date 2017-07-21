// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. 

#ifndef IOTHUB_CLIENT_SAMPLE_MQTT_H
#define IOTHUB_CLIENT_SAMPLE_MQTT_H

#include "iothub_client_ll.h"

void iothubInit(void);
void iothubSendMessage(const unsigned char *, bool);
void iothubLoop(void);
void iothubClose(void);

extern int messageCount;
#endif /* IOTHUB_CLIENT_SAMPLE_MQTT_H */