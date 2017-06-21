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
from os.path import basename, isdir, isfile, join
from shutil import copy
from string import Template
import sys

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-stm32cube")
assert isdir(FRAMEWORK_DIR)

FRAMEWORK_CORE = env.BoardConfig().get("build.mcu")[5:7].lower()
MCU_FAMILY = env.BoardConfig().get("build.mcu")[0:7]

STARTUP_FILE_EXCEPTIONS = {
    "stm32f103c8": "startup_stm32f103xb.s",
    "stm32f103r8": "startup_stm32f103xb.s",
    "stm32f103rc": "startup_stm32f103xb.s"
}


def get_startup_file(mcu):
    if len(mcu) > 12:
        mcu = mcu[:-2]

    search_path = join(
        FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers", "CMSIS", "Device",
        "ST", mcu[0:7].upper() + "xx", "Source", "Templates", "gcc"
    )

    search_path = join(
        search_path,
        "startup_" + mcu[0:9] + "[" + mcu[9] + "|x]" +
        "[" + mcu[10] + "|x]" + ".[sS]"
    )

    if mcu in STARTUP_FILE_EXCEPTIONS:
        return STARTUP_FILE_EXCEPTIONS[mcu]

    startup_file = glob(search_path)

    if not startup_file:
        sys.stderr.write(
            """Error: There is no default startup file for %s MCU!
            Please add initialization code to your project manually!""" % mcu)
        env.Exit(1)
    return basename(startup_file[0])


def get_linker_script(mcu):
    ldscript = join(FRAMEWORK_DIR, "platformio",
                    "ldscripts", mcu[0:11].upper() + "_FLASH.ld")

    if isfile(ldscript):
        return ldscript

    default_ldscript = join(FRAMEWORK_DIR, "platformio",
                            "ldscripts", mcu[0:11].upper() + "_DEFAULT.ld")

    print("Warning! Cannot find a linker script for the required board! "
          "Firmware will be linked with a default linker script!")

    if isfile(default_ldscript):
        return default_ldscript

    ram = env.BoardConfig().get("upload.maximum_ram_size", 0)
    flash = env.BoardConfig().get("upload.maximum_size", 0)
    template_file = join(FRAMEWORK_DIR, "platformio",
                         "ldscripts", "tpl", "linker.tpl")
    content = ""
    with open(template_file) as fp:
        data = Template(fp.read())
        content = data.substitute(
            stack="0x200" + str(hex(ram))[2:],
            ram=str(int(ram/1024)) + "K",
            flash=str(int(flash/1024)) + "K"
        )

    with open(default_ldscript, "w") as fp:
        fp.write(content)

    return default_ldscript


def generate_hal_config_file(mcu):
    config_path = join(FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers",
                       MCU_FAMILY.upper() + "xx_HAL_Driver", "Inc")

    if isfile(join(config_path, MCU_FAMILY + "xx_hal_conf.h")):
        return

    if not isfile(join(config_path, MCU_FAMILY + "xx_hal_conf_template.h")):
        sys.stderr.write(
            "Error: Cannot find template file to configure framework!\n")
        env.Exit(1)

    copy(join(config_path, MCU_FAMILY + "xx_hal_conf_template.h"),
         join(config_path, MCU_FAMILY + "xx_hal_conf.h"))


env.Replace(
    AS="$CC", ASCOM="$ASPPCOM",
    LDSCRIPT_PATH=get_linker_script(env.BoardConfig().get("build.mcu")),
    CPPDEFINES=["USE_HAL_DRIVER"], 
    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ]
)

# restore external build flags
if "build.extra_flags" in env.BoardConfig():
    env.ProcessFlags(env.BoardConfig().get("build.extra_flags"))
# remove base flags
env.ProcessUnFlags(env.get("BUILD_UNFLAGS"))
# apply user flags
env.ProcessFlags(env.get("BUILD_FLAGS"))

env.Append(
    CPPPATH=[
        join(FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers", "CMSIS", "Include"),
        join(FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers", "CMSIS", "Device",
             "ST", MCU_FAMILY.upper() + "xx", "Include"),

        join(FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers",
             MCU_FAMILY.upper() + "xx_HAL_Driver", "Inc")
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, FRAMEWORK_CORE,
             "Drivers", "CMSIS", "Lib", "GCC"),
        join(FRAMEWORK_DIR, "platformio", "ldscripts")
    ]
)

#
# Generate framework specific files
#

generate_hal_config_file(env.BoardConfig().get("build.mcu"))

#
# Target: Build HAL Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkHALDriver"),
    join(FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers",
         MCU_FAMILY.upper() + "xx_HAL_Driver"),
    src_filter="+<*> -<Src/*_template.c>"
))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISDevice"),
    join(FRAMEWORK_DIR, FRAMEWORK_CORE, "Drivers", "CMSIS", "Device", "ST",
         MCU_FAMILY.upper() + "xx", "Source", "Templates"),
    src_filter="-<*> +<*.c> +<gcc/%s>" % get_startup_file(
        env.BoardConfig().get("build.mcu"))
))


env.Append(LIBS=libs)
