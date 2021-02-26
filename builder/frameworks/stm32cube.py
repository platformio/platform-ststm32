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
STM32Cube HAL

STM32Cube embedded software libraries, including:
The HAL hardware abstraction layer, enabling portability between different STM32 devices via standardized API calls
The Low-Layer (LL) APIs, a light-weight, optimized, expert oriented set of APIs designed for both performance and runtime efficiency.

http://www.st.com/en/embedded-software/stm32cube-embedded-software.html?querycriteria=productId=LN1897
"""

import glob
import os
import shutil
import string
import sys

from SCons.Script import DefaultEnvironment

from platformio.builder.tools.piolib import PlatformIOLibBuilder

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

MCU = board.get("build.mcu", "")
MCU_FAMILY = MCU[0:7]

PRODUCT_LINE = board.get("build.product_line", "")
assert PRODUCT_LINE, "Missing MCU or Product Line field"

FRAMEWORK_DIR = platform.get_package_dir("framework-stm32cube%s" % MCU[5:7])
LDSCRIPTS_DIR = platform.get_package_dir("tool-ldscripts-ststm32")
assert all(os.path.isdir(d) for d in (FRAMEWORK_DIR, LDSCRIPTS_DIR))


class CustomLibBuilder(PlatformIOLibBuilder):

    PARSE_SRC_BY_H_NAME = False

    # Max depth of nested includes:
    # -1 = unlimited
    # 0 - disabled nesting
    # >0 - number of allowed nested includes
    CCONDITIONAL_SCANNER_DEPTH = 0

    # For cases when sources located not only in "src" dir
    @property
    def src_dir(self):
        return self.path


def generate_ldscript(default_ldscript_path):
    ram = board.get("upload.maximum_ram_size", 0)
    flash = board.get("upload.maximum_size", 0)
    template_file = os.path.join(LDSCRIPTS_DIR, "tpl", "linker.tpl")
    content = ""
    with open(template_file) as fp:
        data = string.Template(fp.read())
        content = data.substitute(
            stack=hex(0x20000000 + ram),  # 0x20000000 - start address for RAM
            ram=str(int(ram / 1024)) + "K",
            flash=str(int(flash / 1024)) + "K",
        )

    with open(default_ldscript_path, "w") as fp:
        fp.write(content)


def get_linker_script(board_mcu):
    ldscript_match = glob.glob(
        os.path.join(
            LDSCRIPTS_DIR, board_mcu[0:7], board_mcu[0:11].upper() + "*_FLASH.ld"
        )
    )

    if ldscript_match and os.path.isfile(ldscript_match[0]):
        return ldscript_match[0]

    default_ldscript = os.path.join(
        LDSCRIPTS_DIR, board_mcu[0:7], board_mcu[0:11].upper() + "_DEFAULT.ld"
    )

    print(
        "Warning! Cannot find a linker script for the required board! "
        "An auto-generated script will be used to link firmware!"
    )

    if not os.path.isfile(default_ldscript):
        generate_ldscript(default_ldscript)

    return default_ldscript


def prepare_startup_file(src_path):
    startup_file = os.path.join(src_path, "gcc", "startup_%s.S" % PRODUCT_LINE.lower())
    # Change file extension to uppercase
    if not os.path.isfile(startup_file) and os.path.isfile(startup_file[:-2] + ".s"):
        os.rename(startup_file[:-2] + ".s", startup_file)
    if not os.path.isfile(startup_file):
        print(
            "Warning! Cannot find the default startup file for `%s`. "
            "Ignore this warning if the startup code is part of your project." % MCU
        )


def generate_hal_config_file():
    config_path = os.path.join(
        FRAMEWORK_DIR,
        "Drivers",
        MCU_FAMILY.upper() + "xx_HAL_Driver",
        "Inc",
    )

    if os.path.isfile(os.path.join(config_path, MCU_FAMILY + "xx_hal_conf.h")):
        return

    if not os.path.isfile(
        os.path.join(config_path, MCU_FAMILY + "xx_hal_conf_template.h")
    ):
        sys.stderr.write(
            "Error: Cannot find peripheral template file to configure framework!\n"
        )
        env.Exit(1)

    shutil.copy(
        os.path.join(config_path, MCU_FAMILY + "xx_hal_conf_template.h"),
        os.path.join(config_path, MCU_FAMILY + "xx_hal_conf.h"),
    )


def build_custom_lib(lib_path, lib_manifest=None):
    if board.get("build.stm32cube.disable_embedded_libs", "no") == "yes":
        return
    if lib_path:
        lib_manifest = lib_manifest or {"name": os.path.basename(lib_path)}
        env.Append(
            EXTRA_LIB_BUILDERS=[
                PlatformIOLibBuilder(env, lib_path, lib_manifest.copy())
            ]
        )


def build_usb_libs(usb_libs_root):
    # Note: config files for USB peripheral is located in project dirs
    manifest = {
        "build": {
            "flags": ["-I $PROJECT_SRC_DIR", "-I $PROJECT_INCLUDE_DIR"],
            "includeDir": "Inc",
            "srcDir": "Src",
            "srcFilter": ["+<*>", "-<*_template*>"],
        }
    }

    usb_core_dir = os.path.join(usb_libs_root, "Core")
    if os.path.isdir(usb_core_dir):
        manifest["name"] = os.path.basename(usb_libs_root) + "-Core"
        build_custom_lib(usb_core_dir, manifest)

    usb_class_dir = os.path.join(usb_libs_root, "Class")
    if os.path.isdir(usb_class_dir):
        for device_class in os.listdir(usb_class_dir):
            if device_class.lower() == "template":
                continue
            manifest["name"] = "%s-%s" % (os.path.basename(usb_libs_root), device_class)
            build_custom_lib(os.path.join(usb_class_dir, device_class), manifest)


env.Replace(AS="$CC", ASCOM="$ASPPCOM")

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mthumb",
        "-mcpu=%s" % board.get("build.cpu"),
        "-nostdlib",
    ],

    CPPDEFINES=[
        "USE_HAL_DRIVER",
        ("F_CPU", "$BOARD_F_CPU")
    ],

    CPPPATH=[
        "$PROJECT_SRC_DIR",
        "$PROJECT_INCLUDE_DIR",
        os.path.join(FRAMEWORK_DIR, "Drivers", "CMSIS", "DSP", "Include"),
        os.path.join(FRAMEWORK_DIR, "Drivers", "CMSIS", "Include"),
        os.path.join(
            FRAMEWORK_DIR,
            "Drivers",
            "CMSIS",
            "Device",
            "ST",
            MCU_FAMILY.upper() + "xx",
            "Include",
        ),
        os.path.join(
            FRAMEWORK_DIR,
            "Drivers",
            MCU_FAMILY.upper() + "xx_HAL_Driver",
            "Inc",
        ),
        os.path.join(
            FRAMEWORK_DIR,
            "Drivers",
            MCU_FAMILY.upper() + "xx_HAL_Driver",
            "Src",
        ),
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions"
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-mcpu=%s" % board.get("build.cpu"),
        "--specs=nano.specs",
        "--specs=nosys.specs",
    ],

    LIBPATH=[
        os.path.join(FRAMEWORK_DIR, "Drivers", "CMSIS", "Lib", "GCC"),
        os.path.join(FRAMEWORK_DIR, "platformio", "ldscripts"),
    ],

    LIBS=["c", "gcc", "m", "stdc++", "nosys"],
)

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=get_linker_script(board.get("build.mcu", "")))

#
# Process BSP components
#

bsp_dir = os.path.join(FRAMEWORK_DIR, "Drivers", "BSP")
components_dir = os.path.join(bsp_dir, "Components")
for component in os.listdir(components_dir):
    build_custom_lib(os.path.join(components_dir, component))

if os.path.isdir(os.path.join(bsp_dir, "Adafruit_Shield")):
    build_custom_lib(os.path.join(bsp_dir, "Adafruit_Shield"))

#
# Process Utilities
#

utils_dir = os.path.join(FRAMEWORK_DIR, "Utilities")
for util in os.listdir(utils_dir):
    util_dir = os.path.join(utils_dir, util)
    # Some of utilities is not meant to be built
    if not any(f.endswith((".c", ".h")) for f in os.listdir(util_dir)):
        continue
    build_custom_lib(
        os.path.join(utils_dir, util),
        {
            "name": "Util-%s" % util,
            "dependencies": [{"name": "FrameworkVariantBSP"}],
            "build": {"flags": ["-I $PROJECT_SRC_DIR", "-I $PROJECT_INCLUDE_DIR"], "libLDFMode": "deep"},
        },
    )

#
# USB libraries from ST
#

middleware_dir = os.path.join(FRAMEWORK_DIR, "Middlewares", "ST")
for usb_lib in ("STM32_USB_Device_Library", "STM32_USB_Host_Library"):
    build_usb_libs(os.path.join(middleware_dir, usb_lib))

#
# Target: Build HAL Library
#

libs = []

#
# BSP libraries
#

if "build.stm32cube.variant" in board:
    bsp_variant_dir = os.path.join(
        FRAMEWORK_DIR, "Drivers", "BSP", board.get("build.stm32cube.variant")
    )
    if os.path.isdir(bsp_variant_dir):
        build_custom_lib(os.path.join(bsp_variant_dir), {"name": "FrameworkVariantBSP"})

#
# HAL libraries
#

# Generate a default stm32xxx_hal_conf.h
if board.get("build.stm32cube.custom_config_header", "no") == "no":
    generate_hal_config_file()

env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkHALDriver"),
    os.path.join(
        FRAMEWORK_DIR,
        "Drivers",
        MCU_FAMILY.upper() + "xx_HAL_Driver",
    ),
    src_filter="+<*> -<Src/*_template.c> -<Src/Legacy>",
)

#
# CMSIS library
#

if board.get("build.stm32cube.custom_system_setup", "no") == "no":
    sources_path = os.path.join(
        FRAMEWORK_DIR,
        "Drivers",
        "CMSIS",
        "Device",
        "ST",
        MCU_FAMILY.upper() + "xx",
        "Source",
        "Templates",
    )

    prepare_startup_file(sources_path)
    libs.append(
        env.BuildLibrary(
            os.path.join("$BUILD_DIR", "FrameworkCMSISDevice"),
            sources_path,
            src_filter=[
                "-<*>",
                "+<%s>"
                % board.get(
                    "build.stm32cube.system_file", "system_%sxx.c" % MCU_FAMILY
                ),
                "+<gcc/%s>"
                % board.get(
                    "build.stm32cube.startup_file",
                    "startup_%s.S" % PRODUCT_LINE.lower(),
                ),
            ],
        )
    )

env.Append(LIBS=libs)
