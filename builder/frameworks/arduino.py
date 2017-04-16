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

# check Cortex variant to distinguish between F1 and F4 folders
if "m3" in board.get("build.cpu"):
	FRAMEWORK_DIR = join(platform.get_package_dir("framework-arduinoststm32"), "STM32F1")
else:
	FRAMEWORK_DIR = join(platform.get_package_dir("framework-arduinoststm32"), "STM32F4")

FRAMEWORK_VERSION = platform.get_package_version("framework-arduinoststm32")
assert isdir(FRAMEWORK_DIR)

#common build options for F1 and F4
env.Append(
	CCFLAGS=[
		"--param", "max-inline-insns-single=500",
		"-MMD", "-fno-threadsafe-statics"
	],
	
	CPPDEFINES=[
		("ARDUINO", 10612),
		"BOARD_%s" % board.get("build.variant"),
		("DEBUG_LEVEL", "DEBUG_NONE")
	],
	
	CPPPATH=[join(FRAMEWORK_DIR, "cores", board.get("build.core"))],

	LIBPATH=[
		join(FRAMEWORK_DIR, "variants",
			 board.get("build.variant"), "ld")
	],

	LIBS=["c"]
)

# specific build options
if "m3" in board.get("build.cpu"):
	env.Append(
		CCFLAGS=["-march=armv7-m"],

		CPPDEFINES=[
			"__STM32F1__",
			"ARDUINO_ARCH_STM32F1"
		],

		CPPPATH=[
			join(FRAMEWORK_DIR, "system\libmaple"),
			join(FRAMEWORK_DIR, "system\libmaple\include"),
			join(FRAMEWORK_DIR, "system\libmaple\usb\stm32f1"),
			join(FRAMEWORK_DIR, "system\libmaple\usb\usb_lib")
		]
	)
else:
	env.Append(
		CPPDEFINES=[
			"__STM32F4__",
			"ARDUINO_ARCH_STM32F4",
			"VECT_TAB_BASE"
		],

		CPPPATH=[
			join(FRAMEWORK_DIR, "cores", board.get("build.core"), "libmaple"),
			join(FRAMEWORK_DIR, "cores", board.get("build.core"), "libmaple\usbF4"),
			join(FRAMEWORK_DIR, "cores", board.get("build.core"), "libmaple\usbF4\VCP"),
			join(FRAMEWORK_DIR, "cores", board.get("build.core"), "libmaple\usbF4\STM32_USB_OTG_Driver\inc"),
			join(FRAMEWORK_DIR, "cores", board.get("build.core"), "libmaple\usbF4\STM32_USB_Device_Library\Core\inc"),
			join(FRAMEWORK_DIR, "cores", board.get("build.core"), "libmaple\usbF4\STM32_USB_Device_Library\Class\cdc\inc")
		]
	)


for item in ("-nostartfiles", "-nostdlib"):
    if item in env['LINKFLAGS']:
        env['LINKFLAGS'].remove(item)

# upload specific options
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

# error LED handling
if "error_led_port" in board.get("build") and "error_led_pin" in board.get("build"):
	env.Append(CPPDEFINES=[
		("ERROR_LED_PORT", board.get("build.error_led_port")),
		("ERROR_LED_PIN",  board.get("build.error_led_pin"))])
else:
	env.Append(CPPDEFINES=[
		("ERROR_LED_PORT", "GPIOB"),
		("ERROR_LED_PIN", "1")])

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
