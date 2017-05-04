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

from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

if board.id == "bluepill_f103c8":
    board = env.BoardConfig("genericSTM32F103C8")
    env['LDSCRIPT_PATH'] = board.get("build.ldscript")
    env.ProcessFlags(board.get("build.extra_flags"))


FRAMEWORK_DIR = join(platform.get_package_dir(
    "framework-arduinoststm32"), "STM32F1")
FRAMEWORK_VERSION = platform.get_package_version("framework-arduinoststm32")
assert isdir(FRAMEWORK_DIR)

env.Append(
    CCFLAGS=[
        "--param", "max-inline-insns-single=500",
        "-march=armv7-m"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10610),
        "BOARD_%s" % board.get("build.variant"),
        ("ERROR_LED_PORT", "GPIOB"),
        ("ERROR_LED_PIN", 1),
        ("DEBUG_LEVEL", "DEBUG_NONE"),
        "__STM32F1__",
        "ARDUINO_ARCH_STM32F1"
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core")),
        join(FRAMEWORK_DIR, "system", "libmaple"),
        join(FRAMEWORK_DIR, "system", "libmaple", "include"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "stm32f1"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "usb_lib")
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "variants",
             board.get("build.variant"), "ld")
    ],

    LIBS=["c"]
)

for item in ("-nostartfiles", "-nostdlib"):
    if item in env['LINKFLAGS']:
        env['LINKFLAGS'].remove(item)


if env.subst("$UPLOAD_PROTOCOL") == "dfu":
    if board.id in ("maple", "maple_mini_origin"):
        env.Append(CPPDEFINES=[("VECT_TAB_ADDR", 0x8005000), "SERIAL_USB"])
    else:
        env.Append(CPPDEFINES=[
            ("VECT_TAB_ADDR", 0x8002000), "SERIAL_USB", "GENERIC_BOOTLOADER"])

        if "stm32f103r" in board.get("build.mcu", ""):
            env.Replace(LDSCRIPT_PATH="bootloader.ld")
        elif board.get("upload.boot_version", 0) == 2:
            env.Replace(LDSCRIPT_PATH="bootloader_20.ld")
else:
    env.Append(CPPDEFINES=[("VECT_TAB_ADDR", 0x8000000)])


if "__debug" in COMMAND_LINE_TARGETS:
    env.Append(CPPDEFINES=[
        "SERIAL_USB", "GENERIC_BOOTLOADER",
        ("CONFIG_MAPLE_MINI_NO_DISABLE_DEBUG", "1")
    ])

#
# Lookup for specific core's libraries
#

BOARD_CORELIBDIRNAME = board.get("build.core", "")
env.Append(
    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries", "__cores__", BOARD_CORELIBDIRNAME),
        join(FRAMEWORK_DIR, "libraries")
    ]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants",
                 board.get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", board.get("build.core"))
))

env.Prepend(LIBS=libs)
