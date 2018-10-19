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

https://github.com/rogerclarkmelbourne/Arduino_STM32
"""

from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32F4")
assert isdir(FRAMEWORK_DIR)

# default configuration values
vector = int(board.get("build.vec_tab_addr", "0x8000000"), 16)
error_led_port = "GPIOA"
error_led_pin = 7
ldscript = "jtag.ld"
board_type = "discovery_f4"

# remap board configuration values
mcu_type = board.get("build.mcu")[:-2]
if "f407ve" in mcu_type:
    variant = "generic_f407v"
    board_type = "generic_f407v"
elif "f407vg" in mcu_type:
    error_led_port = "GPIOD"
    error_led_pin = 14
    variant = "discovery_f407"

# upload related configuration remap
upload_protocol = env.subst("$UPLOAD_PROTOCOL")

if upload_protocol == "dfu":
    vector = 0x8004000
    if "f407v" in mcu_type:
        ldscript = "bootloader_8004000.ld"

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=["-std=gnu11"],

    CXXFLAGS=[
        "-std=gnu++11",
        "-fno-rtti",
        "-fno-exceptions"
    ],

    CCFLAGS=[
        "-MMD",
        "--param", "max-inline-insns-single=500",
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mthumb",
        "-nostdlib",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu")
    ],

    CPPDEFINES=[
        ("DEBUG_LEVEL", "DEBUG_NONE"),
        ("BOARD_%s" % board_type),
        ("ERROR_LED_PORT", error_led_port),
        ("ERROR_LED_PIN", error_led_pin),
        ("ARDUINO", 10610),
        ("ARDUINO_%s" % variant.upper()),
        ("ARDUINO_ARCH_STM32F4"),
        ("VECT_TAB_FLASH"),
        ("USER_ADDR_ROM", vector),
        ("__STM32F4__"),
        ("STM32_HIGH_DENSITY"),
        ("USB_NC"),
        ("F_CPU", "$BOARD_F_CPU"),
        env.BoardConfig().get("build.variant", "").upper()
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "maple"),
        join(FRAMEWORK_DIR, "cores", "maple", "avr"),
        join(FRAMEWORK_DIR, "cores", "maple", "libmaple"),
        join(FRAMEWORK_DIR, "cores", "maple", "libmaple", "usbF4"),
        join(FRAMEWORK_DIR, "cores", "maple", "libmaple", "usbF4", "VCP"),
        join(FRAMEWORK_DIR, "system", "libmaple"),
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu")
    ],

    LIBPATH=[join(FRAMEWORK_DIR, "variants", variant, "ld")],

    LIBS=["gcc", "m"]
)

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

# remap ldscript
env.Replace(LDSCRIPT_PATH=ldscript)

# remove USB inactive serial flag if other flags are used
if "SERIAL_USB" in env['CPPDEFINES'] or "USB_MSC" in env['CPPDEFINES']:
    env['CPPDEFINES'].remove("USB_NC")

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
