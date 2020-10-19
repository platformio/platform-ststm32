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

https://github.com/microsoft/devkit-sdk
"""

from os import walk
from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.SConscript("../_bare.py")

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
        "-include", "mbed_config.h",
        "-nostdlib"
    ],

    CXXFLAGS=[
        "-std=gnu++11",
        "-fno-threadsafe-statics",
        "-fmessage-length=0",
        "-Wno-missing-field-initializers",
        "-Wno-unused-parameter",
        "-Wvla"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10802),
        ("__MBED__", 1),
        ("DEVICE_I2CSLAVE", 1),
        "TARGET_LIKE_MBED",
        ("DEVICE_PORTOUT", 1),
        ("DEVICE_PORTINOUT", 1),
        "TARGET_RTOS_M4_M7",
        ("DEVICE_LOWPOWERTIMER", 1),
        ("DEVICE_RTC", 1),
        "TOOLCHAIN_object",
        ("DEVICE_SERIAL_ASYNCH", 1),
        "TARGET_STM32F4",
        "__CMSIS_RTOS",
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
        "TARGET_MXCHIP",
        ("DEVICE_SPI", 1),
        "USB_STM_HAL",
        "MXCHIP_LIBRARY",
        ("DEVICE_SPISLAVE", 1),
        ("DEVICE_ANALOGIN", 1),
        ("DEVICE_SERIAL", 1),
        ("DEVICE_ERROR_RED", 1),
        "TARGET_AZ3166",
        "ARM_MATH_CM4",
        ("LPS22HB_I2C_PORT", "MICO_I2C_1"),
        ("DEVICE_STDIO_MESSAGES", 1)
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "system"),
        join(FRAMEWORK_DIR, "system", "az3166-driver"),
        join(FRAMEWORK_DIR, "system", "az3166-driver", "libwlan", "TARGET_EMW1062"),
        join(FRAMEWORK_DIR, "variants",
             board.get("build.variant"), "linker_scripts", "gcc")
    ],

    LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")])


inc_dirs = []
for d in ("system", join("cores", env.BoardConfig().get("build.core"))):
    for root, _, files in sorted(walk(join(FRAMEWORK_DIR, d))):
        if any(f.endswith(".h") for f in files) or "inc" in root:
            if root not in inc_dirs:
                inc_dirs.append(root)

inc_dirs.extend([
    join(FRAMEWORK_DIR, "system"),
    join(FRAMEWORK_DIR, "system", "mbed-os", "features"),
    join(FRAMEWORK_DIR, "system", "mbed-os", "features", "mbedtls"),
    join(FRAMEWORK_DIR, "system", "az3166-driver", "mico", "platform")
])

env.Append(CPPPATH=inc_dirs)

env.Replace(
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
        "--specs=nosys.specs",
        "-u", "_printf_float"
    ]
)

env.Prepend(LIBS=["devkit-sdk-core-lib", "wlan", "stsafe"])
if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=board.get("build.arduino.ldscript", ""))

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
