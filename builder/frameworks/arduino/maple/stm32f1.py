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
    "framework-arduinoststm32"), "STM32F1")
assert isdir(FRAMEWORK_DIR)

# default configuration values
vector = int(board.get("build.vec_tab_addr", "0x8000000"), 16)
error_led_port = "GPIOB"
error_led_pin = 1

# remap board configuration values
mcu_type = board.get("build.mcu")[:-2]
if "f103c8" in mcu_type:
    ldscript = "jtag_c8.ld"
elif "f103cb" in mcu_type or "f103tb" in mcu_type:
    ldscript = "jtag.ld"
elif "f103t8" in mcu_type:
    ldscript = "jtag_t8.ld"
else:
    ldscript = "%s.ld" % mcu_type

if "f103c" in mcu_type:
    variant = "generic_stm32f103c"
elif "f103r8" in mcu_type or "f103rb" in mcu_type:
    variant = "generic_stm32f103r8"
elif "f103rc" in mcu_type or "f103re" in mcu_type:
    variant = "generic_stm32f103r"
elif "f103t8" in mcu_type or "f103tb" in mcu_type:
    variant = "generic_stm32f103t"
elif "f103vb" in mcu_type:
    variant = "generic_stm32f103vb"
elif "f103vc" in mcu_type or "f103ve" in mcu_type or "f103vd" in mcu_type:
    variant = "generic_stm32f103v"
elif "f103z" in mcu_type:
    variant = "generic_stm32f103z"

if "f103v" in mcu_type:
    error_led_port = "GPIOE"
    error_led_pin = 6

# upload related configuration remap
# for all generic boards
upload_protocol = env.subst("$UPLOAD_PROTOCOL")

if upload_protocol not in ("dfu", "serial"):
    env.Append(CPPDEFINES=[
        ("CONFIG_MAPLE_MINI_NO_DISABLE_DEBUG", 1),
        "SERIAL_USB",
        "GENERIC_BOOTLOADER"
    ])

# maple and microduino board related configuration remap
if "maple" in board.id or "microduino" in board.id:
    env.Append(CPPDEFINES=[("SERIAL_USB")])
    vector = 0x8005000
    ldscript = "flash.ld"
    if "microduino" in board.id:
        variant = "microduino"
    elif "maple_mini" in board.id:
        variant = "maple_mini"
    else:
        variant = "maple"

    if board.id == "maple_mini_b20":
        vector = 0x8002000
        ldscript = "bootloader_20.ld"
    elif board.id == "maple_ret6":
        variant = "maple_ret6"
        ldscript = "stm32f103re-bootloader.ld"

# for nucleo f103rb board
elif "nucleo_f103rb" in board.id:
    variant = "nucleo_f103rb"
    ldscript = "jtag.ld"
    env.Append(CPPDEFINES=["NUCLEO_HSE_CRYSTAL"])

elif upload_protocol == "dfu":
    env.Append(CPPDEFINES=["SERIAL_USB", "GENERIC_BOOTLOADER"])
    vector = 0x8002000
    if "f103c" in mcu_type or "f103t" in mcu_type:
        ldscript = "bootloader_20.ld"
    elif "f103r" in mcu_type:
        ldscript = "bootloader.ld"
    elif "f103v" in mcu_type:
        ldscript = "stm32f103veDFU.ld"
    elif "f103z" in mcu_type:
        ldscript = "stm32f103z_dfu.ld"

board_type = variant
if "nucleo_f103rb" in board.id:
    board_type = "STM_NUCLEO_F103RB"
elif "maple_ret6" in board.id:
    board_type = "MAPLE_RET6"
elif "microduino" in board.id:
    board_type = "MICRODUINO_CORE_STM32"

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
        "-march=armv7-m",
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
        ("BOARD_%s" % variant),
        ("VECT_TAB_ADDR", vector),
        ("ERROR_LED_PORT", error_led_port),
        ("ERROR_LED_PIN", error_led_pin),
        ("ARDUINO", 10610),
        ("ARDUINO_%s" % board_type),
        ("ARDUINO_ARCH_STM32F1"),
        ("__STM32F1__"),
        ("MCU_%s" % mcu_type.upper()),
        ("F_CPU", "$BOARD_F_CPU"),
        env.BoardConfig().get("build.variant", "").upper()
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "maple"),
        join(FRAMEWORK_DIR, "system", "libmaple"),
        join(FRAMEWORK_DIR, "system", "libmaple", "include"),
        join(FRAMEWORK_DIR, "system", "libmaple", "stm32f1", "include"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "stm32f1"),
        join(FRAMEWORK_DIR, "system", "libmaple", "usb", "usb_lib")
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu")
    ],

    LIBPATH=[join(FRAMEWORK_DIR, "variants", variant, "ld")],

    LIBS=["c", "gcc", "m", "c"]
)

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

# remap ldscript
env.Replace(LDSCRIPT_PATH=ldscript)

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
