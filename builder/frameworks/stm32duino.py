# Copyright 2014-present Ivan Kravets <me@ikravets.com>
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
STM32duino

STM32 Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://www.stm32duino.com
"""

from os import walk
from os.path import isdir, isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

if "stm32f103" in env.BoardConfig().get("build.mcu", ""):
    FRAMEWORK_DIR = join(platform.get_package_dir("framework-stm32duino"), "STM32F1")
    env.Append(
        CPPDEFINES=[
            "ERROR_LED_PORT=GPIOB",
            "ERROR_LED_PIN=1",
            "ARDUINO_ARCH_STM32F1"
        ]
    )
    if "stm32f103r8" or "stm32f103rb" in env.BoardConfig().get("build.mcu", ""):
        env.Append(CPPDEFINES=["BOARD_generic_stm32f103r8", "ARDUINO_GENERIC_STM32F103R"])
    elif "stm32f103rc" or "stm32f103re" in env.BoardConfig().get("build.mcu", ""):
        env.Append(CPPDEFINES=["BOARD_generic_stm32f103r", "ARDUINO_GENERIC_STM32F103R"])
    elif "stm32f103c" in env.BoardConfig().get("build.mcu", ""):
        env.Append(CPPDEFINES=["BOARD_generic_stm32f103c", "ARDUINO_GENERIC_STM32F103C"])
    elif "stm32f103rb_maple" in env.BoardConfig().get("build.mcu", ""):
        env.Append(CPPDEFINES=["BOARD_maple", "ARDUINO_MAPLE_REV3"])

FRAMEWORK_VERSION = platform.get_package_version("framework-stm32duino")
assert isdir(FRAMEWORK_DIR)

ARDUINO_VERSION = int(FRAMEWORK_VERSION.replace(".", "").strip())

env.Append(
    CPPDEFINES=[
        "ARDUINO=%s" % FRAMEWORK_VERSION.split(".")[1]
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core")),
        join(FRAMEWORK_DIR, "system", "libmaple"),
        join(FRAMEWORK_DIR, "system", "libmaple", "include"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "stm32f1"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "usb_lib")
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"), "ld")
    ]
)

ld = env.BoardConfig().get("build.ldscript")

if env.subst("$UPLOAD_PROTOCOL") == "dfu":
    if "stm32f103c" in env.BoardConfig().get("build.mcu", ""):
        ld = "bootloader_20.ld"
    elif "stm32f103r" in env.BoardConfig().get("build.mcu", ""):
        ld = "bootloader.ld"
    env.Replace(LDSCRIPT_PATH=ld)
    if "stm32f103rb_maple" in env.BoardConfig().get("build.mcu", ""):
        env.Append(CPPDEFINES=["VECT_TAB_ADDR=0x8005000", "SERIAL_USB"])
    else:
        env.Append(CPPDEFINES=["VECT_TAB_ADDR=0x8002000", "SERIAL_USB", "GENERIC_BOOTLOADER"])
else:
    env.Append(CPPDEFINES=["VECT_TAB_ADDR=0x8000000"])
#
# Lookup for specific core's libraries
#

BOARD_CORELIBDIRNAME = env.BoardConfig().get("build.core", "")
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

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ))

envsafe = env.Clone()

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))
))

env.Append(
    LIBPATH=[
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ]
)

env.Prepend(LIBS=libs)
