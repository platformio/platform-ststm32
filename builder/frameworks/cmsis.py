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
CMSIS

The ARM Cortex Microcontroller Software Interface Standard (CMSIS) is a
vendor-independent hardware abstraction layer for the Cortex-M processor
series and specifies debugger interfaces. The CMSIS enables consistent and
simple software interfaces to the processor for interface peripherals,
real-time operating systems, and middleware. It simplifies software
re-use, reducing the learning curve for new microcontroller developers
and cutting the time-to-market for devices.

http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php
"""

import sys
from glob import glob
from string import Template
from os.path import isdir, isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.SConscript("_bare.py")

PLATFORM_NAME = env.get("PIOPLATFORM")
FRAMEWORK_DIR = platform.get_package_dir("framework-cmsis")
assert isdir(FRAMEWORK_DIR)

VARIANT_DIR_EXCEPTIONS = {
    "stm32f103c8": "stm32f103xb",
    "stm32f103r8": "stm32f103xb",
    "stm32f103rc": "stm32f103xb",
    "stm32f103t8": "stm32f103xb",
    "stm32f103vc": "stm32f103xe",
    "stm32f103vd": "stm32f103xe",
    "stm32f103ve": "stm32f103xe",
    "stm32f103zc": "stm32f103xe",
    "stm32f103zd": "stm32f103xe",
    "stm32f303cb": "stm32f303x8",
    "stm32f407ve": "stm32f407xx"
}


def get_variant_dir(mcu):
    if len(mcu) > 12:
        mcu = mcu[:-2]

    mcu_family_path = join(FRAMEWORK_DIR, "variants", PLATFORM_NAME, mcu[0:7])
    mcu_pattern = mcu[0:9] + "[" + mcu[9] + "|x]" + "[" + mcu[10] + "|x]"
    variant_path = join(mcu_family_path, mcu_pattern)
    variant_dirs = glob(variant_path)

    if mcu in VARIANT_DIR_EXCEPTIONS:
        return join(mcu_family_path, VARIANT_DIR_EXCEPTIONS[mcu])

    if not variant_dirs:
        sys.stderr.write(
            """Error: There is no variant dir for %s MCU!
            Please add initialization code to your project manually!""" % mcu)
    return variant_dirs[0]


def get_linker_script(mcu):
    ldscript = join(FRAMEWORK_DIR, "platformio", "ldscripts", PLATFORM_NAME,
                    mcu[0:11].upper() + "_FLASH.ld")

    if isfile(ldscript):
        return ldscript

    default_ldscript = join(FRAMEWORK_DIR, "platformio", "ldscripts",
                            PLATFORM_NAME, mcu[0:11].upper() + "_DEFAULT.ld")

    print("Warning! Cannot find a linker script for the required board! "
          "Firmware will be linked with a default linker script!")

    if isfile(default_ldscript):
        return default_ldscript

    ram = board.get("upload.maximum_ram_size", 0)
    flash = board.get("upload.maximum_size", 0)
    template_file = join(FRAMEWORK_DIR, "platformio",
                         "ldscripts", PLATFORM_NAME, "tpl", "linker.tpl")
    content = ""
    with open(template_file) as fp:
        data = Template(fp.read())
        content = data.substitute(
            stack=hex(0x20000000 + ram),  # 0x20000000 - start address for RAM
            ram=str(int(ram / 1024)) + "K",
            flash=str(int(flash / 1024)) + "K")

    with open(default_ldscript, "w") as fp:
        fp.write(content)

    return default_ldscript

env.Append(CPPPATH=[
    join(FRAMEWORK_DIR, "CMSIS", "Core", "Include"),
    join(FRAMEWORK_DIR, "variants", PLATFORM_NAME,
         board.get("build.mcu")[0:7], "common"),
    join(FRAMEWORK_DIR, "variants", board.get("build.mcu")[0:7],
         board.get("build.mcu"))
])

if not board.get("build.ldscript", ""):
    env.Replace(
        LDSCRIPT_PATH=get_linker_script(board.get("build.mcu")))

#
# Target: Build Core Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    get_variant_dir(board.get("build.mcu"))
))

libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkCMSISCommon"),
        join(FRAMEWORK_DIR, "variants", PLATFORM_NAME,
             board.get("build.mcu")[0:7], "common"))
)

env.Append(LIBS=libs)
