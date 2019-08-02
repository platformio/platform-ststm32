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

from glob import glob
from os import listdir
from os.path import basename, isdir, isfile, join
from shutil import copy
import sys

from SCons.Script import DefaultEnvironment

from platformio import util
from platformio.builder.tools.piolib import PlatformIOLibBuilder

env = DefaultEnvironment()
platform = env.PioPlatform()

board = env.BoardConfig()

if board.get("version", 0) == 2:
    DEVICE_MCU = board.get("device.mcu")
    DEVICE_CPU = board.get("device.cpu")
else:
    DEVICE_MCU = board.get("build.mcu")
    DEVICE_CPU = board.get("build.cpu")

MCU_FAMILY = DEVICE_MCU[0:7].lower()
MCU_CORE = MCU_FAMILY[5:7]

FRAMEWORK_DIR = platform.get_package_dir("framework-stm32cube%s" % MCU_CORE)
assert isdir(FRAMEWORK_DIR)


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


def process_library(lib_name, lib_path, lib_config=None):
    if not isdir(lib_path):
        return

    # usually there are config files in project folders
    config = {
        "name": "%s-lib" % lib_name,
        "build": {
            "flags": ["-I$PROJECTINCLUDE_DIR", "-I$PROJECTSRC_DIR"]
        }
    }
    if lib_config is not None:
        config["build"].update(lib_config.get("build", {}))

    env.Append(
        EXTRA_LIB_BUILDERS=[
            CustomLibBuilder(env, lib_path, config)
        ]
    )


def process_usb_lib(path, lib_name):
    if not isdir(path):
        return

    lib_config = {
        "build": {
            "includeDir": "Inc",
            "srcFilter": "+<*> -<Src/*_template.c>"
        }
    }

    process_library(lib_name, path, lib_config)


def process_usb_classes(usb_class_path, usb_lib):
    if not isdir(usb_class_path):
        return
    for usb_class in listdir(usb_class_path):
        if usb_class.startswith("Template"):
            continue
        process_usb_lib(
            join(usb_class_path, usb_class),
            "Middleware-%s-Class-%s" % (usb_lib, usb_class)
        )


def get_startup_file(mcu):

    if board.get("build.stm32cube.startup_variant", ""):
        return "startup_" + board.get(
            "build.stm32cube.startup_variant") + ".[sS]"

    if len(mcu) > 12:
        mcu = mcu[:-2]

    search_path = join(
        FRAMEWORK_DIR, "Drivers", "CMSIS", "Device",
        "ST", mcu[0:7].upper() + "xx", "Source", "Templates", "gcc"
    )

    search_path = join(
        search_path,
        "startup_" + mcu[0:9] + "[" + mcu[9] + "|x]" +
        "[" + mcu[10] + "|x]" + ".[sS]"
    )

    startup_file = glob(search_path)

    if not startup_file:
        print(
            "Warning: There is no default startup file. " \
            "Add initialization code to your project manually!")

        return "*"

    return basename(startup_file[0])


def get_linker_script(mcu):
    ldscripts = (
        mcu.upper() + "_FLASH.ld",  # new style
        mcu[0:11].upper() + "_FLASH.ld",  # old style
        board.get("build.ldscript", "")  # default from manifest
    )

    for ldscript in ldscripts:
        ldscript_path = join(
            FRAMEWORK_DIR, "platformio", "ldscripts", ldscript)
        if isfile(ldscript):
            return ldscript_path

    # In case when ld script doesn't exist in framework then
    # default ld script is configured during linking by
    # specifying RAM/FLASH sizes as symbols
    env.Append(
        LINKFLAGS=[
            ("-Wl,--defsym=DEVICE_MAX_RAM_SIZE=%s" %
             hex(board.get("upload.maximum_ram_size", 0))),
            ("-Wl,--defsym=DEVICE_FLASH_SIZE=%s" %
             hex(board.get("upload.maximum_size", 0))),
            ("-Wl,--defsym=DEVICE_FLASH_OFFSET=%s" %
             board.get("upload.offset_address", "0x0"))
        ]
    )

    return "STM32_DEFAULT.ld"


def generate_hal_config_file(mcu):
    config_path = join(FRAMEWORK_DIR, "Drivers",
                       MCU_FAMILY.upper() + "xx_HAL_Driver", "Inc")

    # search for user defines config
    search_dirs = (
        env.subst("$PROJECTINCLUDE_DIR"),
        env.subst("$PROJECTSRC_DIR"),
        config_path
    )

    config_name = MCU_FAMILY + "xx_hal_conf.h"

    for d in search_dirs:
        for f in listdir(d):
            if f == config_name:
                # Files from framework depend on this file
                env.Append(CPPPATH=[d])
                return

    # There is no configuration in default paths, so template is used
    if not isfile(join(config_path, "stm32f4xx_hal_conf_template.h")):
        sys.stderr.write(
            "Error: Cannot find template file to configure framework!\n")
        env.Exit(1)

    copy(join(config_path, "stm32f4xx_hal_conf_template.h"),
         join(config_path, config_name))


env.Replace(
    AS="$CC",
    ASCOM="$ASPPCOM",
    LDSCRIPT_PATH=env.subst(get_linker_script(DEVICE_MCU))
)

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mthumb",
        "-mcpu=%s" % DEVICE_CPU,
        "-nostdlib"
    ],

    CPPDEFINES=[
        "USE_HAL_DRIVER",
        ("F_CPU", "$BOARD_F_CPU")
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions"
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-mcpu=%s" % DEVICE_CPU,
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ],

    LIBS=["c", "gcc", "m", "stdc++", "nosys"]
)

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

env.ProcessFlags(board.get("build.stm32cube.extra_flags", ""))

cpp_flags = env.Flatten(env.get("CPPDEFINES", []))

if "F103xC" in cpp_flags:
    env.Append(CPPDEFINES=["STM32F103xE"])
elif "F103x8" in cpp_flags:
    env.Append(CPPDEFINES=["STM32F103xB"])


env.Append(
    CPPPATH=[
        join(FRAMEWORK_DIR, "Drivers", "CMSIS", "Include"),
        join(FRAMEWORK_DIR, "Drivers", "CMSIS", "Device",
             "ST", MCU_FAMILY.upper() + "xx", "Include"),

        join(FRAMEWORK_DIR, "Drivers",
             MCU_FAMILY.upper() + "xx_HAL_Driver", "Inc"),
        join(FRAMEWORK_DIR, "Drivers",
             "BSP", "Components", "Common")
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR,
             "Drivers", "CMSIS", "Lib", "GCC"),
        join(FRAMEWORK_DIR, "platformio", "ldscripts")
    ]
)

variants_remap = util.load_json(
    join(FRAMEWORK_DIR, "platformio", "variants_remap.json"))
board_type = env.subst("$BOARD")
variant = variants_remap[
    board_type] if board_type in variants_remap else board_type.upper()

variant_dir = join(FRAMEWORK_DIR, "Drivers", "BSP", variant)
if isdir(variant_dir):
    env.Append(CPPPATH=[variant_dir])
    process_library("BSP-variant", variant_dir)

#
# Generate framework specific file with enabled modules
#

generate_hal_config_file(DEVICE_MCU)

#
# Process BSP components
#

components_dir = join(
    FRAMEWORK_DIR, "Drivers", "BSP", "Components")
for component in listdir(components_dir):
    process_library(component, join(components_dir, component))

if isdir(join(FRAMEWORK_DIR, "Drivers", "BSP", "Adafruit_Shield")):
    process_library(
        "BSP-Adafruit_Shield",
        join(FRAMEWORK_DIR, "Drivers", "BSP", "Adafruit_Shield")
    )

#
# Process USB libraries
#

for usb_lib in ("STM32_USB_Device_Library", "STM32_USB_Host_Library"):
    usblib_dir = join(FRAMEWORK_DIR, "Middlewares", "ST", usb_lib)
    usblib_core_dir = join(usblib_dir, "Core")
    process_usb_lib(usblib_core_dir, usb_lib)
    process_usb_classes(join(usblib_dir, "Class"), usb_lib)

#
# Utility libraries
#

utilities_dir = join(FRAMEWORK_DIR, "Utilities")
if isdir(utilities_dir):
    for utility in listdir(utilities_dir):
        process_library(utility, join(utilities_dir, utility))

if isdir(join(FRAMEWORK_DIR, "Middlewares", "Third_Party", "FatFs")):
    fatfs_config = dict()
    fatfs_config["build"] = {
        "srcFilter": "+<*> -<drivers> -<option> -<*_template.c>"
    }
    process_library(
        "Third_Party-FatFs",
        join(FRAMEWORK_DIR, "Middlewares", "Third_Party", "FatFs", "src"),
        fatfs_config
    )

#
# Target: Build HAL Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkHALDriver"),
    join(FRAMEWORK_DIR, "Drivers",
         MCU_FAMILY.upper() + "xx_HAL_Driver"),
    src_filter="+<*> -<Src/*_template.c> -<Src/Legacy>"
))

if "PIO_STM32CUBE_CUSTOM_STARTUP" not in cpp_flags:
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkCMSISDevice"),
        join(FRAMEWORK_DIR, "Drivers", "CMSIS", "Device", "ST",
             MCU_FAMILY.upper() + "xx", "Source", "Templates"),
        src_filter="-<*> +<*.c> +<gcc/%s>" % get_startup_file(DEVICE_MCU)
    ))

env.Prepend(LIBS=libs)
