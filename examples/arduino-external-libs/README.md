How to build PlatformIO based project
=====================================

1. [Install PlatformIO Core](http://docs.platformio.org/page/core.html)
2. Download [development platform with examples](https://github.com/platformio/platform-ststm32/archive/develop.zip)
3. Extract ZIP archive
4. Run these commands:

```shell
# Change directory to example
$ cd platform-ststm32/examples/arduino-external-libs

# Build project
$ pio run

# Upload firmware
$ pio run --target upload

# Build specific environment
$ pio run -e maple

# Upload firmware for the specific environment
$ pio run -e maple --target upload

# Clean build files
$ pio run --target clean
```
