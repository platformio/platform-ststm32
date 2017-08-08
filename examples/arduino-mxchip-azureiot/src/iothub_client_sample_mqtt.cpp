// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. 

#include "AzureIotHub.h"
#include "Arduino.h"
#include "config.h"
#include "utility.h"
#include "EEPROMInterface.h"
#include "iothub_client_sample_mqtt.h"
#include <ArduinoJson.h>

static IOTHUB_CLIENT_LL_HANDLE iotHubClientHandle;
static bool messagePending = false;
static bool messageSending = true;

static IOTHUBMESSAGE_DISPOSITION_RESULT c2dMessageCallback(IOTHUB_MESSAGE_HANDLE message, void *userContextCallback)
{
    const char *buffer;
    size_t size;

    if (IoTHubMessage_GetByteArray(message, (const unsigned char **)&buffer, &size) != IOTHUB_MESSAGE_OK)
    {
        LogInfo("unable to IoTHubMessage_GetByteArray");
        return IOTHUBMESSAGE_REJECTED;
    }
    else
    {
        char *temp = (char *)malloc(size + 1);
        if (temp == NULL)
        {
            LogInfo("Failed to malloc for command");
            return IOTHUBMESSAGE_REJECTED;
        }
        memcpy(temp, buffer, size);
        temp[size] = '\0';
        LogInfo("Receive C2D message: %s", temp);
        blinkLED();
        free(temp);
        return IOTHUBMESSAGE_ACCEPTED;
    }
}

static void twinCallback(DEVICE_TWIN_UPDATE_STATE updateState, const unsigned char *payLoad, size_t size, void *userContextCallback)
{
    char *temp = (char *)malloc(size + 1);
    for (int i = 0; i < size; i++)
    {
        temp[i] = (char)(payLoad[i]);
    }
    temp[size] = '\0';
    parseTwinMessage(temp);
    free(temp);
}

void start()
{
    LogInfo("Start sending temperature and humidity data");
    messageSending = true;
}

void stop()
{
    LogInfo("Stop sending temperature and humidity data");
    messageSending = false;
}

const char *onSuccess = "\"Successfully invoke device method\"";
const char *notFound = "\"No method found\"";

int deviceMethodCallback(const char *methodName, const unsigned char *payload, size_t size, unsigned char **response, size_t *response_size, void *userContextCallback)
{
    LogInfo("Try to invoke method %s", methodName);
    const char *responseMessage = onSuccess;
    int result = 200;

    if (strcmp(methodName, "start") == 0)
    {
        start();
    }
    else if (strcmp(methodName, "stop") == 0)
    {
        stop();
    }
    else
    {
        LogInfo("No method %s found", methodName);
        responseMessage = notFound;
        result = 404;
    }

    *response_size = strlen(responseMessage);
    *response = (unsigned char *)malloc(*response_size);
    strncpy((char *)(*response), responseMessage, *response_size);

    return result;
}

void iothubInit()
{
    srand((unsigned int)time(NULL));

    // Load connection from EEPROM
    EEPROMInterface eeprom;
    uint8_t connString[AZ_IOT_HUB_MAX_LEN + 1] = { '\0' };
    int ret = eeprom.read(connString, AZ_IOT_HUB_MAX_LEN, 0x00, AZ_IOT_HUB_ZONE_IDX);
    if (ret < 0)
    { 
        LogInfo("ERROR: Unable to get the azure iot connection string from EEPROM. Please set the value in configuration mode.");
        return;
    }
    else if (ret == 0)
    {
        LogInfo("INFO: The connection string is empty. Please set the value in configuration mode.");
        return;
    }

    if (platform_init() != 0)
    {
        LogInfo("Failed to initialize the platform.");
        return;
    }

    if ((iotHubClientHandle = IoTHubClient_LL_CreateFromConnectionString((char*)connString, MQTT_Protocol)) == NULL)
    {
        LogInfo("iotHubClientHandle is NULL!");
        return;
    }

    if (IoTHubClient_LL_SetOption(iotHubClientHandle, "TrustedCerts", certificates) != IOTHUB_CLIENT_OK)
    {
        LogInfo("failure to set option \"TrustedCerts\"");
        return;
    }

    if (IoTHubClient_LL_SetMessageCallback(iotHubClientHandle, c2dMessageCallback, NULL) != IOTHUB_CLIENT_OK)
    {
        LogInfo("IoTHubClient_LL_SetMessageCallback FAILED!");
        return;
    }
    if (IoTHubClient_LL_SetDeviceTwinCallback(iotHubClientHandle, twinCallback, NULL) != IOTHUB_CLIENT_OK)
    {
        LogInfo("Failed on IoTHubClient_LL_SetDeviceTwinCallback");
        return;
    }

    if(IoTHubClient_LL_SetDeviceMethodCallback(iotHubClientHandle, deviceMethodCallback, NULL) != IOTHUB_CLIENT_OK)
    {
        LogInfo("Failed on IoTHubClient_LL_SetDeviceMethodCallback");
        return;
    }    
}

static void sendConfirmationCallback(IOTHUB_CLIENT_CONFIRMATION_RESULT result, void *userContextCallback)
{
    if (IOTHUB_CLIENT_CONFIRMATION_OK == result)
    {
        LogInfo("Message sent to Azure IoT Hub");
        blinkSendConfirmation();
    }
    else
    {
        LogInfo("Failed to send message to Azure IoT Hub");
    }
    messageCount++;
    messagePending = false;
}

void iothubSendMessage(const unsigned char *text, bool temperatureAlert)
{
    if (messageSending && !messagePending)
    {
        IOTHUB_MESSAGE_HANDLE messageHandle = IoTHubMessage_CreateFromByteArray(text, strlen((const char *)text));
        if (messageHandle == NULL)
        {
            LogInfo("unable to create a new IoTHubMessage");
            return;
        }
        MAP_HANDLE properties = IoTHubMessage_Properties(messageHandle);
        Map_Add(properties, "temperatureAlert", temperatureAlert ? "true" : "false");
        LogInfo("Sending message: %s", text);
        if (IoTHubClient_LL_SendEventAsync(iotHubClientHandle, messageHandle, sendConfirmationCallback, NULL) != IOTHUB_CLIENT_OK)
        {
            LogInfo("Failed to hand over the message to IoTHubClient");
            return;
        }
        LogInfo("IoTHubClient accepted the message for delivery");
        messagePending = true;
        IoTHubMessage_Destroy(messageHandle);
        delay(getInterval());
    }
}

void iothubLoop(void)
{
    IoTHubClient_LL_DoWork(iotHubClientHandle);
}
