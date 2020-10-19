#include "AZ3166WiFi.h"
#include "http_client.h"
#include "IoT_DevKit_HW.h"
#include "SystemVersion.h"
#include "SystemTickCounter.h"
#include "telemetry.h"

#define NUMSENSORS 5 // 5 sensors to display

// 0 - Humidity & Temperature Sensor
// 1 - Pressure Sensor
// 2 - Magnetic Sensor
// 3 - Gyro Sensor
// 4 - Motion (Acceleration) Sensor
static int status;
static bool showSensor;
static bool isConnected;
static unsigned char counter;

static char buffInfo[128];
static int buttonAState = 0;
static int buttonBState = 0;

#define READ_ENV_INTERVAL 2000
static volatile uint64_t msReadEnvData = 0;

static const char GITHUB_CERT[] =
    "-----BEGIN CERTIFICATE-----\r\nMIIDxTCCAq2gAwIBAgIQAqxcJmoLQJuPC3nyrkYldzANBgkqhkiG9w0BAQUFADBs\r\nMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3\r\nd3cuZGlnaWNlcnQuY29tMSswKQYDVQQDEyJEaWdpQ2VydCBIaWdoIEFzc3VyYW5j\r\nZSBFViBSb290IENBMB4XDTA2MTExMDAwMDAwMFoXDTMxMTExMDAwMDAwMFowbDEL\r\nMAkGA1UEBhMCVVMxFTATBgNVBAoTDERpZ2lDZXJ0IEluYzEZMBcGA1UECxMQd3d3\r\nLmRpZ2ljZXJ0LmNvbTErMCkGA1UEAxMiRGlnaUNlcnQgSGlnaCBBc3N1cmFuY2Ug\r\nRVYgUm9vdCBDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMbM5XPm\r\n+9S75S0tMqbf5YE/yc0lSbZxKsPVlDRnogocsF9ppkCxxLeyj9CYpKlBWTrT3JTW\r\nPNt0OKRKzE0lgvdKpVMSOO7zSW1xkX5jtqumX8OkhPhPYlG++MXs2ziS4wblCJEM\r\nxChBVfvLWokVfnHoNb9Ncgk9vjo4UFt3MRuNs8ckRZqnrG0AFFoEt7oT61EKmEFB\r\nIk5lYYeBQVCmeVyJ3hlKV9Uu5l0cUyx+mM0aBhakaHPQNAQTXKFx01p8VdteZOE3\r\nhzBWBOURtCmAEvF5OYiiAhF8J2a3iLd48soKqDirCmTCv2ZdlYTBoSUeh10aUAsg\r\nEsxBu24LUTi4S8sCAwEAAaNjMGEwDgYDVR0PAQH/BAQDAgGGMA8GA1UdEwEB/wQF\r\nMAMBAf8wHQYDVR0OBBYEFLE+w2kD+L9HAdSYJhoIAu9jZCvDMB8GA1UdIwQYMBaA\r\nFLE+w2kD+L9HAdSYJhoIAu9jZCvDMA0GCSqGSIb3DQEBBQUAA4IBAQAcGgaX3Nec\r\nnzyIZgYIVyHbIUf4KmeqvxgydkAQV8GK83rZEWWONfqe/EW1ntlMMUu4kehDLI6z\r\neM7b41N5cdblIZQB2lWHmiRk9opmzN6cN82oNLFpmyPInngiK3BD41VHMWEZ71jF\r\nhS9OMPagMRYjyOfiZRYzy78aG6A9+MpeizGLYAiJLQwGXFK3xPkKmNEVX58Svnw2\r\nYzi9RKR/5CYrCsSXaQ3pjOLAEFe4yHYSkVXySGnYvCoCWw9E1CAx2/S6cCZdkGCe\r\nvEsXCS+0yx5DaMkHJ8HSXPfqIbloEpw8nL+e/IBcm2PN7EeqJSdnoDfzAIJ9VNep\r\n+OkuE6N36B9K\r\n-----END CERTIFICATE-----\r\n";
static const char *FIRMWARE_VERSION_PATH = "https://microsoft.github.io/azure-iot-developer-kit/firmware.txt";

void getLatestFirmwareVersion()
{
  char buffTelemetry[64];

  HTTPClient client = HTTPClient(GITHUB_CERT, HTTP_GET, FIRMWARE_VERSION_PATH);
  const Http_Response *response = client.send(NULL, 0);
  if (response != NULL)
  {
    snprintf(buffTelemetry, sizeof(buffTelemetry), "Local: %s, Remote: %s", getDevkitVersion(), response->body);

    // Microsoft collects data to operate effectively and provide you the best experiences with our products.
    // We collect data about the features you use, how often you use them, and how you use them.
    send_telemetry_data("", "SensorStatusFirmwareVersionSucceeded", buffTelemetry);

    if (strcmp(response->body, getDevkitVersion()) == 0)
    {
      snprintf(buffInfo, sizeof(buffInfo), "IoT DevKit\r\nCurrent: %s\r\n \r\nBtn B: Sensors\r\n", getDevkitVersion());
    }
    else
    {
      snprintf(buffInfo, sizeof(buffInfo), "IoT DevKit\r\nCurrent: %s\r\nLatest: %s\r\nBtn B: Sensors\r\n", getDevkitVersion(), response->body);
    }
  }
  else
  {
    snprintf(buffTelemetry, sizeof(buffTelemetry), "Local: %s", getDevkitVersion());

    // Microsoft collects data to operate effectively and provide you the best experiences with our products.
    // We collect data about the features you use, how often you use them, and how you use them.
    send_telemetry_data("", "SensorStatusFirmwareVersionFailed", buffTelemetry);

    snprintf(buffInfo, sizeof(buffInfo), "IoT DevKit\r\nCurrent: %s\r\nLatest: N/A\r\nBtn B: Sensor\r\n", getDevkitVersion());
  }
  textOutDevKitScreen(0, buffInfo, 1);
}

void showMotionGyroSensor()
{
  int x, y, z;
  getDevKitGyroscopeValue(&x, &y, &z);
  snprintf(buffInfo, sizeof(buffInfo), "Gyroscope \r\n    x:%d   \r\n    y:%d   \r\n    z:%d  ", x, y, z);
  textOutDevKitScreen(0, buffInfo, 1);
}

void showMotionAccelSensor()
{
  int x, y, z;
  getDevKitAcceleratorValue(&x, &y, &z);
  snprintf(buffInfo, sizeof(buffInfo), "Accelerometer \r\n    x:%d   \r\n    y:%d   \r\n    z:%d  ", x, y, z);
  textOutDevKitScreen(0, buffInfo, 1);
}

void showPressureSensor()
{
  uint64_t ms = SystemTickCounterRead() - msReadEnvData;
  if (ms < READ_ENV_INTERVAL)
  {
    return;
  }

  float pressure = getDevKitPressureValue();
  snprintf(buffInfo, sizeof(buffInfo), "Environment\r\nPressure: \r\n   %0.2f hPa\r\n  ", pressure);
  textOutDevKitScreen(0, buffInfo, 1);
  msReadEnvData = SystemTickCounterRead();
}

void showHumidTempSensor()
{
  uint64_t ms = SystemTickCounterRead() - msReadEnvData;
  if (ms < READ_ENV_INTERVAL)
  {
    return;
  }
  float tempC = getDevKitTemperatureValue(0);
  float tempF = tempC * 1.8 + 32;
  float humidity = getDevKitHumidityValue();

  snprintf(buffInfo, sizeof(buffInfo), "Environment \r\n Temp:%0.2f F \r\n      %0.2f C \r\n Humidity:%0.2f%%", tempF, tempC, humidity);
  textOutDevKitScreen(0, buffInfo, 1);

  msReadEnvData = SystemTickCounterRead();
}

void showMagneticSensor()
{
  int x, y, z;
  getDevKitMagnetometerValue(&x, &y, &z);
  snprintf(buffInfo, sizeof(buffInfo), "Magnetometer \r\n    x:%d   \r\n    y:%d   \r\n    z:%d  ", x, y, z);
  textOutDevKitScreen(0, buffInfo, 1);
}

void ShowTips()
{
  IPAddress ip = WiFi.localIP();
  snprintf(buffInfo, sizeof(buffInfo), "Who said\r\nCogito ergo\r\nsum?\r\n%s\r\n", ip.get_address());
  textOutDevKitScreen(0, buffInfo, 1);
}

void setup()
{
  status = 4;
  counter = 0;
  showSensor = false;
  isConnected = false;
  msReadEnvData = 0;

  int ret = initIoTDevKit(1);
  if (ret == 0)
  {
    // Everthing OK
    isConnected = true;

    //Scan networks and print them into console
    int numSsid = WiFi.scanNetworks();
    for (int thisNet = 0; thisNet < numSsid; thisNet++)
    {
      Serial.print(thisNet);
      Serial.print(") ");
      Serial.print(WiFi.SSID(thisNet));
      Serial.print("\tSignal: ");
      Serial.print(WiFi.RSSI(thisNet));
      Serial.print("\tEnc type: ");
      Serial.println(WiFi.encryptionType(thisNet));
    }
    // Get IP address
    IPAddress ip = WiFi.localIP();
    snprintf(buffInfo, sizeof(buffInfo), "WiFi Connected\r\n%s\r\n%s\r\n \r\n", WiFi.SSID(), ip.get_address());
    textOutDevKitScreen(0, buffInfo, 1);

    // Get firmware version
    getLatestFirmwareVersion();

    // Enable blinking
    startBlinkDevKitRGBLED(-1);
    startBlinkDevKitUserLED(-1);
  }
  else
  {
    cleanDevKitScreen();
    // Something wrong
    switch (ret)
    {
    case -100:
      textOutDevKitScreen(0, "No WiFi\r\nEnter AP Mode\r\nto config", 1);
      break;
    case -101:
      textOutDevKitScreen(0, "Init failed\r\n I2C", 1);
      break;
    case -102:
      textOutDevKitScreen(0, "Init failed\r\n LSM6DSL\r\n   sensor", 1);
      break;
    case -103:
      textOutDevKitScreen(0, "Init failed\r\n HTS221\r\n   sensor", 1);
      break;
    case -104:
      textOutDevKitScreen(0, "Init failed\r\n LIS2MDL\r\n   sensor", 1);
      break;
    case -105:
      textOutDevKitScreen(0, "Init failed\r\n IRDA", 1);
      break;
    case -106:
      textOutDevKitScreen(0, "Init failed\r\n LPS22HB\r\n   sensor", 1);
      break;
    }
  }
}

void loop()
{
  if (isConnected)
  {
    if (getButtonBState())
    {
      // Button B is pushed down
      buttonBState = 1;
    }
    else
    {
      // Button B is released
      if (buttonBState)
      {
        // One click
        // Switch to show sensor data
        status = (status + 1) % NUMSENSORS;
        showSensor = true;
        msReadEnvData = 0;
        buttonBState = 0;
        counter = 0;
      }
    }

    if (getButtonAState())
    {
      // Button A is pushed down
      buttonAState = 1;
    }
    else
    {
      // Button A is released
      if (buttonAState)
      {
        // One click
        // Switch to shwo IP address
        showSensor = false;
        ShowTips();
        buttonAState = 0;
      }
    }

    if ((counter % 1000) == 0)
    {
      // Test the onboard IrDA for each 10s
      int irda_status = transmitIrDA(&counter, sizeof(counter), 100);
      if (irda_status != 0)
      {
        Serial.println("Unable to transmit through IRDA");
      }
    }
    if ((counter % 50) == 0)
    {
      // Update sensor data on the screen for each 0.5s
      if (showSensor)
      {
        switch (status)
        {
        case 0:
          showHumidTempSensor();
          break;
        case 1:
          showPressureSensor();
          break;
        case 2:
          showMagneticSensor();
          break;
        case 3:
          showMotionGyroSensor();
          break;
        case 4:
          showMotionAccelSensor();
          break;
        }
      }
    }
  }

  invokeDevKitPeripheral();
  counter++;
  delay(10);
}
