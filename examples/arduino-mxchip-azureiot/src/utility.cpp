// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. 

#include "HTS221Sensor.h"
#include "AzureIotHub.h"
#include "Arduino.h"
#include <ArduinoJson.h>
#include "config.h"
#include "RGB_LED.h"

#define RGB_LED_BRIGHTNESS 32

DevI2C *i2c;
HTS221Sensor *sensor;
static RGB_LED rgbLed;
static int interval = INTERVAL;

int getInterval()
{
    return interval;
}

void blinkLED()
{
    rgbLed.turnOff();
    rgbLed.setColor(RGB_LED_BRIGHTNESS, 0, 0);
    delay(500);
    rgbLed.turnOff();
}

void blinkSendConfirmation()
{
    rgbLed.turnOff();
    rgbLed.setColor(0, 0, RGB_LED_BRIGHTNESS);
    delay(500);
    rgbLed.turnOff();
}

void parseTwinMessage(const char *message)
{
    StaticJsonBuffer<MESSAGE_MAX_LEN> jsonBuffer;
    JsonObject &root = jsonBuffer.parseObject(message);
    if (!root.success())
    {
        LogError("parse %s failed", message);
        return;
    }

    if (root["desired"]["interval"].success())
    {
        interval = root["desired"]["interval"];
    }
    else if (root.containsKey("interval"))
    {
        interval = root["interval"];
    }
}

void sensorInit()
{
    i2c = new DevI2C(D14, D15);
    sensor = new HTS221Sensor(*i2c);
    sensor->init(NULL);
}

float readTemperature()
{
    sensor->reset();

    float temperature = 0;
    sensor->getTemperature(&temperature);

    return temperature;
}

float readHumidity()
{
    sensor->reset();

    float humidity = 0;
    sensor->getHumidity(&humidity);

    return humidity;
}

bool readMessage(int messageId, char *payload)
{
    float temperature = readTemperature();
    float humidity = readHumidity();
    StaticJsonBuffer<MESSAGE_MAX_LEN> jsonBuffer;
    JsonObject& root = jsonBuffer.createObject();
    root["deviceId"] = DEVICE_ID;
    root["messageId"] = messageId;
    bool temperatureAlert = false;

    if(temperature != temperature)
    {
        root["temperature"] = NULL;
    }
    else
    {
        root["temperature"] = temperature;
        if(temperature > TEMPERATURE_ALERT)
        {
            temperatureAlert = true;
        }
    }

    if(humidity != humidity)
    {
        root["humidity"] = NULL;
    }
    else
    {
        root["humidity"] = humidity;
    }
    root.printTo(payload, MESSAGE_MAX_LEN);
    return temperatureAlert;
}