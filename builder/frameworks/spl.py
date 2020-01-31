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
SPL

The ST Standard Peripheral Library provides a set of functions for
handling the peripherals on the STM32 Cortex-M3 family.
The idea is to save the user (the new user, in particular) having to deal
directly with the registers.

http://www.st.com/web/en/catalog/tools/FM147/CL1794/SC961/SS1743?sc=stm32embeddedsoftware
"""

from os.path import isdir, isfile, join
from string import Template

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.SConscript("_bare.py")

FRAMEWORK_DIR = platform.get_package_dir("framework-spl")
assert isdir(FRAMEWORK_DIR)


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

    ram = board.get("upload.maximum_ram_size", 0)
    flash = board.get("upload.maximum_size", 0)
    template_file = join(FRAMEWORK_DIR, "platformio",
                         "ldscripts", "tpl", "linker.tpl")
    content = ""
    with open(template_file) as fp:
        data = Template(fp.read())
        content = data.substitute(
            stack=hex(0x20000000 + ram), # 0x20000000 - start address for RAM
            ram=str(int(ram/1024)) + "K",
            flash=str(int(flash/1024)) + "K"
        )

    with open(default_ldscript, "w") as fp:
        fp.write(content)

    return default_ldscript

env.Append(
    CPPPATH=[
        join(FRAMEWORK_DIR, board.get("build.core"),
             "cmsis", "cores", board.get("build.core")),
        join(FRAMEWORK_DIR, board.get("build.core"), "cmsis",
             "variants", board.get("build.mcu")[0:7]),
        join(FRAMEWORK_DIR, board.get("build.core"), "spl",
             "variants", board.get("build.mcu")[0:7], "inc"),
        join(FRAMEWORK_DIR, board.get("build.core"), "spl",
             "variants", board.get("build.mcu")[0:7], "src")
    ]
)

env.Append(
    CPPDEFINES=[
        "USE_STDPERIPH_DRIVER"
    ]
)

if not board.get("build.ldscript", ""):
    env.Replace(
        LDSCRIPT_PATH=get_linker_script(board.get("build.mcu")))

#
# Target: Build SPL Library
#

extra_flags = board.get("build.extra_flags", "")
src_filter_patterns = ["+<*>"]
if "STM32F40_41xxx" in extra_flags:
    src_filter_patterns += ["-<stm32f4xx_fmc.c>"]
if "STM32F427_437xx" in extra_flags:
    src_filter_patterns += ["-<stm32f4xx_fsmc.c>"]
elif "STM32F303xC" in extra_flags:
    src_filter_patterns += ["-<stm32f30x_hrtim.c>"]
elif "STM32L1XX_MD" in extra_flags:
    src_filter_patterns += ["-<stm32l1xx_flash_ramfunc.c>"]

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(
        FRAMEWORK_DIR, board.get("build.core"), "cmsis",
        "variants", board.get("build.mcu")[0:7]
    )
))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join(FRAMEWORK_DIR, board.get("build.core"),
         "spl", "variants",
         board.get("build.mcu")[0:7], "src"),
    src_filter=" ".join(src_filter_patterns)
))

env.Append(LIBS=libs)
