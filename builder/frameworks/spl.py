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

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-spl")
assert isdir(FRAMEWORK_DIR)

env.Append(
    CPPPATH=[
        join(FRAMEWORK_DIR, env.BoardConfig().get("build.core"),
             "cmsis", "cores", env.BoardConfig().get("build.core")),
        join(FRAMEWORK_DIR, env.BoardConfig().get("build.core"), "cmsis",
             "variants", env.BoardConfig().get("build.variant")[0:7]),
        join(FRAMEWORK_DIR, env.BoardConfig().get("build.core"), "spl",
             "variants", env.BoardConfig().get("build.variant")[0:7], "inc"),
        join(FRAMEWORK_DIR, env.BoardConfig().get("build.core"), "spl",
             "variants", env.BoardConfig().get("build.variant")[0:7], "src")
    ]
)

envsafe = env.Clone()

envsafe.Append(
    CPPDEFINES=[
        "USE_STDPERIPH_DRIVER"
    ]
)

#
# Target: Build SPL Library
#

# use mbed ldscript with bootloader section
ldscript = env.BoardConfig().get("build.ldscript")
if not isfile(join(platform.get_dir(), "ldscripts", ldscript)):
    if "mbed" in env.BoardConfig().get("frameworks", []):
        env.Append(
            LINKFLAGS=[
                '-Wl,-T"%s"' %
                join(
                    platform.get_package_dir("framework-mbed"), "targets",
                    "TARGET_STM", "TARGET_%s" % env.BoardConfig().get("build.variant")[:7],
                    "TARGET_%s" % env.subst("$BOARD").upper(), "device",
                    "TOOLCHAIN_GCC_ARM", "%s.ld" % ldscript.upper()[:-3]
                )
            ]
        )

extra_flags = env.BoardConfig().get("build.extra_flags", "")
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

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(
        FRAMEWORK_DIR, env.BoardConfig().get("build.core"), "cmsis",
        "variants", env.BoardConfig().get("build.variant")[0:7]
    )
))

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join(FRAMEWORK_DIR, env.BoardConfig().get("build.core"),
         "spl", "variants",
         env.BoardConfig().get("build.variant")[0:7], "src"),
    src_filter=" ".join(src_filter_patterns)
))

env.Append(LIBS=libs)
