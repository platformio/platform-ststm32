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

https://github.com/stm32duino/Arduino_Core_STM32
"""

from os.path import isdir, join

from SCons.Script import DefaultEnvironment
from platformio import util

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32")
CMSIS_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32", "CMSIS", "CMSIS")
assert isdir(FRAMEWORK_DIR)
assert isdir(CMSIS_DIR)


mcu_type = board.get("build.mcu")[:-2]
variant = board.get("build.variant")
series = mcu_type[:7].upper() + "xx"
variant_dir = join(FRAMEWORK_DIR, "variants", variant)

if any(mcu in board.get("build.cpu") for mcu in ("cortex-m4", "cortex-m7")):
    env.Append(
        CCFLAGS=[
            "-mfpu=fpv4-sp-d16",
            "-mfloat-abi=hard"
        ],

        LINKFLAGS=[
            "-mfpu=fpv4-sp-d16",
            "-mfloat-abi=hard"
        ]
    )

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=[
        "-std=gnu11"
    ],

    CXXFLAGS=[
        "-std=gnu++14",
        "-fno-threadsafe-statics",
        "-fno-rtti",
        "-fno-exceptions"
    ],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
        "-mthumb",
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-nostdlib",
        "--param", "max-inline-insns-single=500"
    ],

    CPPDEFINES=[
        series,
        "HAL_UART_MODULE_ENABLED",
        ("ARDUINO", 10805),
        ("ARDUINO_%s" % variant),
        ("ARDUINO_ARCH_STM32"),
        ("BOARD_NAME", variant),
        env.BoardConfig().get("build.variant", "").upper()
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "arduino", "avr"),
        join(FRAMEWORK_DIR, "cores", "arduino", "stm32"),
        join(FRAMEWORK_DIR, "cores", "arduino", "stm32", "LL"),
        join(FRAMEWORK_DIR, "system", "Drivers",
             series + "_HAL_Driver", "Inc"),
        join(FRAMEWORK_DIR, "system", "Drivers",
             series + "_HAL_Driver", "Src"),
        join(FRAMEWORK_DIR, "system", series),
        join(variant_dir, "usb"),
        join(FRAMEWORK_DIR, "system", "Middlewares", "ST",
             "STM32_USB_Device_Library", "Core", "Inc"),
        join(FRAMEWORK_DIR, "system", "Middlewares", "ST",
             "STM32_USB_Device_Library", "Core", "Src"),
        join(FRAMEWORK_DIR, "system", "Middlewares", "ST",
             "STM32_USB_Device_Library", "Class", "CDC", "Inc"),
        join(FRAMEWORK_DIR, "system", "Middlewares", "ST",
             "STM32_USB_Device_Library", "Class", "CDC", "Src"),
        join(CMSIS_DIR, "Core", "Include"),
        join(FRAMEWORK_DIR, "system", "Drivers", "CMSIS",
             "Device", "ST", series, "Include"),
        join(FRAMEWORK_DIR, "system", "Drivers", "CMSIS",
             "Device", "ST", series, "Source", "Templates", "gcc"),
        join(FRAMEWORK_DIR, "cores", "arduino"),
        variant_dir
    ],

    LINKFLAGS=[
        "-Os",
        "-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
        "--specs=nano.specs",
        "-Wl,--gc-sections,--relax",
        "-Wl,--check-sections",
        "-Wl,--entry=Reset_Handler",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBS=[
        "arm_cortex%sl_math" % board.get("build.cpu")[7:9].upper(),
        "c", "m", "gcc", "stdc++", "c"  # two libc in order to fix linker error
    ],

    LIBPATH=[
        variant_dir,
        join(CMSIS_DIR, "Lib", "GCC")
    ]
)

#
# Configure Serial interface
#

if "PIO_FRAMEWORK_ARDUINO_SERIAL_DISABLED" in env.Flatten(
        env.get("CPPDEFINES", [])):
    env['CPPDEFINES'].remove("FFFFFHAL_UART_MODULE_ENABLED")

elif "PIO_FRAMEWORK_ARDUINO_SERIAL_WITHOUT_GENERIC" in env.Flatten(
        env.get("CPPDEFINES", [])):
    env.Append(CPPDEFINES=["HWSERIAL_NONE"])

#
# Configure standard library
#

if "PIO_FRAMEWORK_ARDUINO_STANDARD_LIB" in env.Flatten(
        env.get("CPPDEFINES", [])):
    env['LINKFLAGS'].remove("--specs=nano.specs")
if "PIO_FRAMEWORK_ARDUINO_NANOLIB_FLOAT_PRINTF" in env.Flatten(
        env.get("CPPDEFINES", [])):
    env.Append(LINKFLAGS=["-u_printf_float"])
if "PIO_FRAMEWORK_ARDUINO_NANOLIB_FLOAT_SCANF" in env.Flatten(
        env.get("CPPDEFINES", [])):
    env.Append(LINKFLAGS=["-u_scanf_float"])

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

# remap ldscript
env.Replace(LDSCRIPT_PATH="ldscript.ld")

env.Append(
    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries", "__cores__", "arduino"),
        join(FRAMEWORK_DIR, "libraries")
    ]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[variant_dir]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        variant_dir
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", "arduino")
))

env.Prepend(LIBS=libs)
