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

from os.path import isdir, isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-cmsis")
assert isdir(FRAMEWORK_DIR)

env.Append(
    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core")),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get(
             "build.variant")[0:7], "common"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get(
             "build.variant")[0:7], env.BoardConfig().get("build.variant"))
    ]
)

envsafe = env.Clone()

#
# Target: Build Core Library
#

# use mbed ldscript with bootloader section
ldscript = env.BoardConfig().get("build.ldscript")
if not isfile(join(platform.get_dir(), "ldscripts", ldscript)):
    if "mbed" in env.BoardConfig().get("frameworks", []):
        env.Append(
            LINKFLAGS=[
                '-Wl,-T"%s"' %
                join(
                    platform.get_package_dir("framework-mbed"), "variant",
                    env.subst("$BOARD").upper(), "mbed",
                    "TARGET_%s" % env.subst("$BOARD").upper(),
                    "TOOLCHAIN_GCC_ARM", "%s.ld" % ldscript.upper()[:-3]
                )
            ]
        )

libs = []
libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(
        FRAMEWORK_DIR, "variants",
        env.BoardConfig().get("build.variant")[0:7],
        env.BoardConfig().get("build.variant")
    )
))

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISCommon"),
    join(
        FRAMEWORK_DIR, "variants",
        env.BoardConfig().get("build.variant")[0:7], "common"
    )
))

env.Append(LIBS=libs)
