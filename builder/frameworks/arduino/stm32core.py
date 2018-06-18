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

FRAMEWORK_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32")
CMSIS_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32", "CMSIS", "CMSIS")
assert isdir(FRAMEWORK_DIR)
assert isdir(CMSIS_DIR)

# default configuration values
env.Append(CPPDEFINES=["HAL_UART_MODULE_ENABLED"])

mcu_type = board.get("build.mcu")[:-2]
variant = board.id.upper()
series = mcu_type[:7].upper() + "xx"
m = board.get("build.cpu")[7:9].upper() + "l_math"
library = "arm_" + board.get("build.cpu")[:6] + m

# mcu's that require additional flags
mcu_list = [ 
    "f429", "l496", "f302", "f303re",
    "f401", "f411", "f446", "l476",
    "l432"
]

for item in mcu_list:
    if item in mcu_type:
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

if "DISCO_L475VG_IOT01A" in variant:
    variant = "DISCO_L475VG_IOT"
elif "MAPLE_MINI" in variant:
    variant = "BLUEPILL_F103C8"

# remap serialx configuration
if "XSERIAL_ENABLED" in env['CPPDEFINES']:
    env.Append(CPPDEFINES=["HWSERIAL_NONE"])
elif "XSERIAL_DISABLED" in env['CPPDEFINES']: 
    env['CPPDEFINES'].remove("HAL_UART_MODULE_ENABLED")

# remove unused flags
for item in ("STM32F1", "STM32F4", "STM32F40_41xxx", "STM32L053xx"):
    if item in env['CPPDEFINES']:
        env['CPPDEFINES'].remove(item)

for item in env['CPPDEFINES']:
    if "F_CPU" in item:
        env['CPPDEFINES'].remove(item)

for item in ("-nostartfiles", "-nostdlib"):
    if item in env['LINKFLAGS']:
        env['LINKFLAGS'].remove(item)

for item in env['LIBS']:
    if "nosys" in item:
        env['LIBS'].remove(item)

env.Append(
    CFLAGS=["-std=gnu11", "-Dprintf=iprintf"],

    CXXFLAGS=["-std=gnu++14", "-fno-threadsafe-statics"],

    CCFLAGS=["-MMD", "--param", "max-inline-insns-single=500"],

    CPPDEFINES=[
        (series),
        ("ARDUINO", 10805),
        ("ARDUINO_%s" % variant),
        ("ARDUINO_ARCH_STM32"),
        ("BOARD_NAME=\"%s\"" % variant),
        (board.get("build.extra_flags"))
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "arduino", "avr"),
        join(FRAMEWORK_DIR, "cores", "arduino", "stm32"),
        join(FRAMEWORK_DIR, "system", "Drivers", series + "_HAL_Driver", "Inc"),
        join(FRAMEWORK_DIR, "system", "Drivers", series + "_HAL_Driver", "Src"),
        join(FRAMEWORK_DIR, "system", series),
        join(FRAMEWORK_DIR, "variants", variant, "usb"),
        join(FRAMEWORK_DIR, "system", "Middlewares", "ST", 
            "STM32_USB_Device_Library", "Core", "Inc"),
        join(FRAMEWORK_DIR, "system", "Middlewares", "ST", 
            "STM32_USB_Device_Library", "Core", "Src"),
        join(FRAMEWORK_DIR, CMSIS_DIR, "Core", "Include"),
        join(FRAMEWORK_DIR, "system", "Drivers", "CMSIS", 
            "Device", "ST", series, "Include"),
        join(FRAMEWORK_DIR, "system", "Drivers", "CMSIS", 
            "Device", "ST", series, "Source", "Templates", "gcc"),
        join(FRAMEWORK_DIR, "cores", "arduino"),
        join(FRAMEWORK_DIR, "variants", variant)
    ],

    LINKFLAGS=[
        "-Wl,--check-sections",
        "-Wl,--entry=Reset_Handler",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align",
        "--specs=nano.specs"
    ],

    LIBS=["c", library],

    LIBPATH=[
        join(FRAMEWORK_DIR, "variants", variant),
        join(FRAMEWORK_DIR, CMSIS_DIR, "Lib", "GCC")
    ]
)

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

if "build.variant" in board:
    env.Append(
        CPPPATH=[join(FRAMEWORK_DIR, "variants", variant)]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", variant)
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", "arduino")
))

env.Prepend(LIBS=libs)
