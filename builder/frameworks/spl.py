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
import sys
from os.path import isdir, isfile, join
from string import Template

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.SConscript("_bare.py")

FRAMEWORK_DIR = platform.get_package_dir("framework-spl")
assert isdir(FRAMEWORK_DIR)

mcu = board.get("build.mcu").lower()

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
            stack=hex(0x20000000 + ram),  # 0x20000000 - start address for RAM
            ram=str(int(ram / 1024)) + "K",
            flash=str(int(flash / 1024)) + "K"
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
    ],
    LINKFLAGS=[
        "-nostartfiles"
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
cmsis_variant_filter_patterns = ["+<*>"]
if "STM32F40_41xxx" in extra_flags:
    src_filter_patterns += ["-<stm32f4xx_fmc.c>"]
if "STM32F427_437xx" in extra_flags:
    src_filter_patterns += ["-<stm32f4xx_fsmc.c>"]
elif "STM32F303xC" in extra_flags:
    src_filter_patterns += ["-<stm32f30x_hrtim.c>"]
elif "STM32L1XX_MD" in extra_flags:
    src_filter_patterns += ["-<stm32l1xx_flash_ramfunc.c>"]

# generate filer expression for F10x startup file
if mcu.startswith("stm32f10"):
    # stm32f10x SPL has 8 possible startup files
    # depending on the series (connectivity, low/high/medium/extra-large density or 
    # "value-line").
    # but, there are no value-line (STM32F100xx) chips in this platform yet.
    # we only want to assemble and link the correct one.
    # we automatically deduce the correct startup file and identifying macro based
    # on MCU name and flash size, which saves us from adapting tons of boards files.
    # for details see page 90 of reference manual and stm32f10x.h.
    # https://www.st.com/resource/en/reference_manual/cd00171190-stm32f101xx-stm32f102xx-stm32f103xx-stm32f105xx-and-stm32f107xx-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf
    flash_mem = board.get("upload.maximum_size") // 1024
    family = mcu[0:9] # only get the chip family as e.g. stm32f103
    startup_file, series_macro = (None, None)
    # give user the possibility to give the startup file themselves as a fallback
    # then the identifying macro is also expected to be given.
    startup_file = board.get("build.spl_startup_file", "")
    if startup_file == "":
        if family in ("stm32f101", "stm32f102", "stm32f103") and flash_mem >= 16 and flash_mem <= 32:
            startup_file, series_macro = ("startup_stm32f10x_ld.S", "STM32F10X_LD") # low density
        elif family in ("stm32f101", "stm32f102", "stm32f103") and flash_mem >= 64 and flash_mem <= 128:
            startup_file, series_macro = ("startup_stm32f10x_md.S", "STM32F10X_MD") # medium density
        elif family in ("stm32f101", "stm32f103") and flash_mem >= 256 and flash_mem <= 512:
                startup_file, series_macro = ("startup_stm32f10x_hd.S", "STM32F10X_HD") # high density
        elif family in ("stm32f101", "stm32f103") and flash_mem >= 768 and flash_mem <= 1024:
                startup_file, series_macro = ("startup_stm32f10x_xl.S", "STM32F10X_XL") # xtra-large density
        elif family in ("stm32f105", "stm32f107"):
                startup_file, series_macro = ( "startup_stm32f10x_cl.S", "STM32F10X_CD") # connectivity line

    if startup_file is None:
            sys.stderr.write("Failed to find startup file for board '%s'.\n" % board.id)
            env.Exit(-1)
    # exclude all startup files via wildcard, add back the one we want
    cmsis_variant_filter_patterns += ["-<startup_stm32f10x_*.S>", "+<%s>" % startup_file]
    if series_macro is not None:
        env.Append(CPPDEFINES=[series_macro])

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(
        FRAMEWORK_DIR, board.get("build.core"), "cmsis",
        "variants", board.get("build.mcu")[0:7]
    ),
    src_filter=cmsis_variant_filter_patterns
))

# STM32F1 SPL introduced updated core_cm3.c that needs
# to be compiled for Cortex-M3 cores.
if board.get("build.cpu") == "cortex-m3":
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkCMSISCore"),
        join(
            FRAMEWORK_DIR, board.get("build.core"), "cmsis",
            "cores", "stm32"
        ),
        src_filter="+<core_cm3.c>"
    ))


libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join(FRAMEWORK_DIR, board.get("build.core"),
         "spl", "variants",
         board.get("build.mcu")[0:7], "src"),
    src_filter=" ".join(src_filter_patterns)
))

env.Append(LIBS=libs)
