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

import glob
import os
import string

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
mcu = board.get("build.mcu", "")
product_line = board.get("build.product_line", "")
assert product_line, "Missing MCU or Product Line field"

env.SConscript("_bare.py")

CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_DEVICE_DIR = platform.get_package_dir("framework-cmsis-" + mcu[0:7])
LDSCRIPTS_DIR = platform.get_package_dir("tool-ldscripts-ststm32")
assert all(os.path.isdir(d) for d in (CMSIS_DIR, CMSIS_DEVICE_DIR, LDSCRIPTS_DIR))


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
            flash=str(int(flash / 1024)) + "K")

    with open(default_ldscript_path, "w") as fp:
        fp.write(content)


def get_linker_script():
    ldscript_match = glob.glob(os.path.join(
        LDSCRIPTS_DIR, mcu[0:7], mcu[0:11].upper() + "*_FLASH.ld"))

    if ldscript_match and os.path.isfile(ldscript_match[0]):
        return ldscript_match[0]

    default_ldscript = os.path.join(
        LDSCRIPTS_DIR, mcu[0:7], mcu[0:11].upper() + "_DEFAULT.ld")

    print("Warning! Cannot find a linker script for the required board! "
          "An auto-generated script will be used to link firmware!")

    if not os.path.isfile(default_ldscript):
        generate_ldscript(default_ldscript)

    return default_ldscript


def prepare_startup_file(src_path):
    startup_file = os.path.join(src_path, "gcc", "startup_%s.S" % product_line.lower())
    # Change file extension to uppercase:
    if not os.path.isfile(startup_file) and os.path.isfile(startup_file[:-2] + ".s"):
        os.rename(startup_file[:-2] + ".s", startup_file)
    if not os.path.isfile(startup_file):
        print("Warning! Cannot find the default startup file for %s. "
              "Ignore this warning if the startup code is part of your project." % mcu)


#
# Allow using custom linker scripts
#

if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=get_linker_script())

#
# Prepare build environment
#

# The final firmware is linked against standard library with two specifications:
# nano.specs - link against a reduced-size variant of libc
# nosys.specs - link against stubbed standard syscalls

env.Append(
    CPPPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Include"),
        os.path.join(CMSIS_DEVICE_DIR, "Include")
    ],

    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ]
)

#
# Compile CMSIS sources
#

sources_path = os.path.join(CMSIS_DEVICE_DIR, "Source", "Templates")
prepare_startup_file(sources_path)

env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkCMSIS"), sources_path,
    src_filter=[
        "-<*>",
        "+<%s>" % board.get("build.cmsis.system_file", "system_%sxx.c" % mcu[0:7]),
        "+<gcc/startup_%s.S>" % product_line.lower()]
)
