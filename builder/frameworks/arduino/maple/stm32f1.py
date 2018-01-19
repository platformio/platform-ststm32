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

Import("env")
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32F1")
FRAMEWORK_VERSION = platform.get_package_version("framework-arduinoststm32")
assert isdir(FRAMEWORK_DIR)

# default configuration values
vector = 0x8000000
error_led_port = "GPIOB"
error_led_pin = 1

# remap board configuration values
mcu_type = board.get("build.mcu")[:-2]
if "f103c8" in mcu_type:
    ldscript = "jtag_c8.ld"
elif "f103cb" in mcu_type:
    ldscript = "jtag.ld"
else:
    ldscript = "%s.ld" % mcu_type

if "f103c" in mcu_type:
    variant = "generic_stm32f103c"
elif "f103r8" in mcu_type or "f103rb" in mcu_type:
    variant = "generic_stm32f103r8"
elif "f103rc" in mcu_type or "f103re" in mcu_type:
    variant = "generic_stm32f103r"

# upload related configuration remap
if not board.id in "maple":
    # for all boards except maple ones
    if env.subst("$UPLOAD_PROTOCOL") == "dfu":
        vector = 0x8002000
        env.Append(CPPDEFINES=["SERIAL_USB", "GENERIC_BOOTLOADER"])

        if "f103c" in mcu_type:
            ldscript = "bootloader_20.ld"
        elif "f103r" in mcu_type:
            ldscript = "bootloader.ld"
    elif env.subst("$UPLOAD_PROTOCOL") == "stlink":
        env.Append(CPPDEFINES=[
            ("CONFIG_MAPLE_MINI_NO_DISABLE_DEBUG", 1), 
            "SERIAL_USB", 
            "GENERIC_BOOTLOADER"
        ])
    else:
        env.Append(CPPDEFINES=[("CONFIG_MAPLE_MINI_NO_DISABLE_DEBUG", 1)])

        if board.get("build.vec_tab_addr", "") :
            vector = int(board.get("build.vec_tab_addr"), 16)
else:
    # maple board related configuration remap
    if board.id in "maple":
        env.Append(CPPDEFINES=[("SERIAL_USB")])
        variant = "maple_mini" if board.id in "maple_mini" else "maple"
        vector = 0x8002000
        ldscript = "bootloader_20"

        if board.id in "maple_mini_origin" or board.id in "maple":
            vector = 0x8005000
            ldscript = "flash.ld"

env.Append(
    CFLAGS=["-std=gnu11"],

    CXXFLAGS=["-std=gnu++11"],

    CCFLAGS=[
        "-MMD",
        "--param", "max-inline-insns-single=500",
        "-march=armv7-m"
    ],

    CPPDEFINES=[
        ("DEBUG_LEVEL", "DEBUG_NONE"),
        ("BOARD_%s" % variant),
        ("VECT_TAB_ADDR", vector),
        ("ERROR_LED_PORT", error_led_port),
        ("ERROR_LED_PIN", error_led_pin),
        ("ARDUINO", 10610),
        ("ARDUINO_%s" % variant.upper()),
        ("ARDUINO_ARCH_STM32F1"),
        ("__STM32F1__"),
        ("MCU_%s" % mcu_type.upper())
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "maple"),
        join(FRAMEWORK_DIR, "system", "libmaple"),
        join(FRAMEWORK_DIR, "system", "libmaple", "include"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "stm32f1"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "usb_lib")
    ],

    LIBPATH=[join(FRAMEWORK_DIR, "variants", variant, "ld")]
)

# remap ldscript
env.Replace(LDSCRIPT_PATH=[ldscript])

# remove unused linker flags
for item in ("-nostartfiles", "-nostdlib"):
    if item in env['LINKFLAGS']:
        env['LINKFLAGS'].remove(item)

# remove unused libraries
for item in ("c", "stdc++", "nosys"):
    if item in env['LIBS']:
        env['LIBS'].remove(item)

#
# Lookup for specific core's libraries
#

env.Append(
    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries", "__cores__", "maple"),
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
    join(FRAMEWORK_DIR, "cores", "maple")
))

env.Prepend(LIBS=libs)
