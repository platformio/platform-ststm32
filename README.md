# ST STM32: development platform for [PlatformIO](http://platformio.org)

[![Build Status](https://github.com/platformio/platform-ststm32/workflows/Examples/badge.svg)](https://github.com/platformio/platform-ststm32/actions)

The STM32 family of 32-bit Flash MCUs based on the ARM Cortex-M processor is designed to offer new degrees of freedom to MCU users. It offers a 32-bit product range that combines very high performance, real-time capabilities, digital signal processing, and low-power, low-voltage operation, while maintaining full integration and ease of development.

* [Home](http://platformio.org/platforms/ststm32) (home page in PlatformIO Platform Registry)
* [Documentation](http://docs.platformio.org/page/platforms/ststm32.html) (advanced usage, packages, boards, frameworks, etc.)

# Usage

1. [Install PlatformIO](http://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](http://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = ststm32
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/platformio/platform-ststm32.git
board = ...
...
```

# Configuration

Please navigate to [documentation](http://docs.platformio.org/page/platforms/ststm32.html).
