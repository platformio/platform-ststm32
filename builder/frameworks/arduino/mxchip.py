# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://www.stm32duino.com
"""

from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinostm32mxchip")
FRAMEWORK_VERSION = platform.get_package_version(
    "framework-arduinostm32mxchip")
assert isdir(FRAMEWORK_DIR)

env.Append(
    CFLAGS=["-std=gnu99"],

    CCFLAGS=[
        "-w",
        "--param", "max-inline-insns-single=500",
        "-mfloat-abi=softfp",
        "-mfpu=fpv4-sp-d16",
        "-include", "mbed_config.h"
    ],

    CXXFLAGS=[
        "-Wextra",
        "-std=gnu++11",
        "-fno-threadsafe-statics",
        "-fmessage-length=0",
        "-Wno-missing-field-initializers",
        "-Wno-unused-parameter",
        "-Wvla"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10802),
        ("FRAMEWORK_ARDUINO", int(FRAMEWORK_VERSION.replace(".", "0"))),
        ("__MBED__", 1),
        ("DEVICE_I2CSLAVE", 1),
        "TARGET_LIKE_MBED",
        ("LWIP_TIMEVAL_PRIVATE", 0),
        ("DEVICE_PORTOUT", 1),
        "USBHOST_OTHER",
        ("DEVICE_PORTINOUT", 1),
        "TARGET_RTOS_M4_M7",
        ("DEVICE_LOWPOWERTIMER", 1),
        ("DEVICE_RTC", 1),
        "TOOLCHAIN_object",
        ("DEVICE_SERIAL_ASYNCH", 1),
        "TARGET_STM32F4",
        "__CMSIS_RTOS",
        "TARGET_EMW1062",
        "TOOLCHAIN_GCC",
        ("DEVICE_CAN", 1),
        "TARGET_CORTEX_M",
        "TARGET_DEBUG",
        ("DEVICE_I2C_ASYNCH", 1),
        "TARGET_LIKE_CORTEX_M4",
        "TARGET_M4",
        "TARGET_UVISOR_UNSUPPORTED",
        ("DEVICE_QSPI", 1),
        ("DEVICE_SPI_ASYNCH", 1),
        ("MBED_BUILD_TIMESTAMP", "1490085708.63"),
        ("DEVICE_PWMOUT", 1),
        ("DEVICE_INTERRUPTIN", 1),
        ("DEVICE_I2C", 1),
        ("TRANSACTION_QUEUE_SIZE_SPI", 2),
        "__CORTEX_M4",
        ("HSE_VALUE", '\"((uint32_t)26000000)\"'),
        "TARGET_FF_MORPHO",
        ("__FPU_PRESENT", 1),
        "TARGET_FF_ARDUINO",
        ("DEVICE_PORTIN", 1),
        "TARGET_STM",
        ("DEVICE_SERIAL_FC", 1),
        ("DEVICE_SDIO", 1),
        ("DEVICE_TRNG", 1),
        "__MBED_CMSIS_RTOS_CM",
        ("DEVICE_SLEEP", 1),
        "TOOLCHAIN_GCC_ARM",
        ("TARGET_MXCHIP", 1),
        ("DEVICE_SPI", 1),
        "USB_STM_HAL",
        "MXCHIP_LIBRARY",
        ("DEVICE_SPISLAVE", 1),
        ("DEVICE_ANALOGIN", 1),
        ("DEVICE_SERIAL", 1),
        ("DEVICE_ERROR_RED", 1),
        "TARGET_AZ3166",
        "ARM_MATH_CM4",
        ("LPS22HB_I2C_PORT", "MICO_I2C_1")
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "system", "sdk", "lib"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "libwlan",
             "TARGET_EMW1062"),
        join(FRAMEWORK_DIR, "variants",
             board.get("build.variant"), "linker_scripts", "gcc")
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "system"),
        join(FRAMEWORK_DIR, "system", "drivers"),
        join(FRAMEWORK_DIR, "system", "cmsis"),
        join(FRAMEWORK_DIR, "system", "hal"),
        join(FRAMEWORK_DIR, "system", "rtos"),
        join(FRAMEWORK_DIR, "system", "events"),
        join(FRAMEWORK_DIR, "system", "EEPROMInterface"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "TARGET_AZ3166"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "include"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "include",
             "mico_drivers"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "platform"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "platform",
             "include"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "platform",
             "mbed"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "system"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "net", "LwIP",
             "lwip-sys"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "net", "LwIP",
             "lwip-ver1.4.0.rc1", "src", "include"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "net", "LwIP",
             "lwip-ver1.4.0.rc1", "src", "include", "lwip"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "mico", "net", "LwIP",
             "lwip-ver1.4.0.rc1", "src", "include", "ipv4"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "libraries",
             "utilities"),
        join(FRAMEWORK_DIR, "system", "emw10xx-driver", "libraries", "drivers",
             "display", "VGM128064"),
        join(FRAMEWORK_DIR, "system", "features"),
        join(FRAMEWORK_DIR, "system", "features", "filesystem"),
        join(FRAMEWORK_DIR, "system", "features", "filesystem", "bd"),
        join(FRAMEWORK_DIR, "system", "features", "filesystem", "fat"),
        join(FRAMEWORK_DIR, "system", "features", "filesystem", "fat", "ChaN"),
        join(FRAMEWORK_DIR, "system", "features", "netsocket"),
        join(FRAMEWORK_DIR, "system", "features", "mbedtls"),
        join(FRAMEWORK_DIR, "system", "features", "mbedtls", "inc"),
        join(FRAMEWORK_DIR, "system", "features", "mbedtls", "inc", "mbedtls"),
        join(FRAMEWORK_DIR, "system", "targets", "TARGET_STM"),
        join(FRAMEWORK_DIR, "system", "targets", "TARGET_STM",
             "TARGET_STM32F4"),
        join(FRAMEWORK_DIR, "system", "targets", "TARGET_STM",
             "TARGET_STM32F4", "device"),
        join(FRAMEWORK_DIR, "system", "targets", "TARGET_MXCHIP",
             "TARGET_AZ3166"),
        join(FRAMEWORK_DIR, "system", "targets", "TARGET_MXCHIP",
             "TARGET_AZ3166", "device"),
        join(FRAMEWORK_DIR, "system", "rtos", "rtx", "TARGET_CORTEX_M"),
        join(FRAMEWORK_DIR, "system", "platform"),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core")),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"),
             "cli"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "NTPClient"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "json-c"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "az_iot", "c-utility",
             "inc"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "az_iot", "azure_umqtt_c",
             "inc"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "httpserver"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "httpclient"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "httpclient", "http_parser"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "az_iot", "iothub_client",
             "inc"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "system"),
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "az_iot")
    ],

    LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")])

env.Replace(
    LIBS=["m", "wlan", "wifi", "mbed-os", "stdc++", "gcc"],

    LINKFLAGS=[
        "-mcpu=cortex-m4",
        "-mthumb",
        "-Wl,--check-sections",
        "-Wl,--gc-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align",
        "-Wl,--wrap,_malloc_r",
        "-Wl,--wrap,_free_r",
        "-Wl,--wrap,_realloc_r",
        "-Wl,--wrap,_calloc_r",
        "-Wl,--start-group",
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ],

    UPLOADER="openocd",
    UPLOADERFLAGS=[
        "-s", join(platform.get_package_dir("tool-openocd") or "",
                   "scripts"),
        "-s", join(platform.get_package_dir("tool-openocd") or "",
                   "scripts", "interface"),
        "-f", "stlink-v2-1.cfg",

        "-s", join(platform.get_package_dir("tool-openocd") or "",
                   "scripts", "target"),
        "-f", "stm32f4x.cfg",

        "-c", "transport select hla_swd",
        "-c", "program {{$SOURCES}} verify reset 0x8008000; shutdown"
    ],

    UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS'
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(CPPPATH=[
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ])

    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "FrameworkArduinoVariant"),
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))))

libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduino"),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))))

env.Prepend(LIBS=libs)
