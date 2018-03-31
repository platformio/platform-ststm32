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
    "framework-arduinoststm32"), "STM32F4")
assert isdir(FRAMEWORK_DIR)

# default configuration values
error_led_port = "GPIOA"
error_led_pin = 7

# remap board configuration values
mcu_type = board.get("build.mcu")[:-2]
if "stm32f407ve" in mcu_type:
    ldscript = "jtag.ld"
    variant = "generic_f407v"


# upload related configuration remap
# for all generic boards
upload_protocol = env.subst("$UPLOAD_PROTOCOL")

env.Append(
    CFLAGS=[
        "-mthumb",
        "-MMD",
        "-std=gnu11",
        "-nostdlib",
        "--param",
        "max-inline-insns-single=500"],

    CXXFLAGS=[
        "-mthumb",
        "-MMD",
        "-std=gnu++11",
        "-nostdlib",
        "-fno-rtti",
        "-fno-exceptions",
        "--param",
        "max-inline-insns-single=500"],

    CPPDEFINES=[
        ("DEBUG_LEVEL", "DEBUG_NONE"),
        ("BOARD_%s" % variant),
        ("ERROR_LED_PORT", error_led_port),
        ("ERROR_LED_PIN", error_led_pin),
        ("ARDUINO", 10610),
        ("ARDUINO_%s" % variant.upper()
            if not "nucleo" in board.id else "STM_NUCLEO_F103RB"),
        ("ARDUINO_ARCH_STM32F4"),
        ("VECT_TAB_FLASH"),
        ("USER_ADDR_ROM=0x08000000"),
        ("__STM32F4__"),
        ("MCU_%s" % mcu_type.upper()),
        ("SERIAL_USB") # this is so that usb serial is connected when the board boots, use USB_MSC for having USB Mass Storage (MSC) instead
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "maple"),
        join(FRAMEWORK_DIR, "cores", "maple", "avr"),
        join(FRAMEWORK_DIR, "cores", "maple", "libmaple"),
        join(FRAMEWORK_DIR, "cores", "maple", "libmaple", "usbF4"),
        join(FRAMEWORK_DIR, "cores", "maple", "libmaple", "usbF4", "VCP"),
        join(FRAMEWORK_DIR, "system", "libmaple"),
    ],

    LIBPATH=[join(FRAMEWORK_DIR, "variants", variant, "ld")],

    LIBS=["c"]
)

# remap ldscript
env.Replace(LDSCRIPT_PATH=ldscript)

# remove unused linker flags
for item in ("-nostartfiles", "-nostdlib"):
    if item in env['LINKFLAGS']:
        env['LINKFLAGS'].remove(item)

# remove unused libraries
for item in ("stdc++", "nosys"):
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
