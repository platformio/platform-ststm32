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

from os.path import basename, isfile, join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)


env = DefaultEnvironment()

env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],

    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-g",   # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
		"-Wall",
        "-mthumb",
        "-nostdlib"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions"
    ],

    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU")
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-Wl,-Map,output.map",
        "-mthumb",
        "-nostartfiles",
        "-nostdlib"
    ],

    LIBS=["c", "gcc", "m", "stdc++", "nosys"],

    UPLOADER="st-flash",
    UPLOADERFLAGS=[
        "write",        # write in flash
        "$SOURCES",     # firmware path to flash
        "0x08000000"    # flash start address
    ],
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS',

    SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',

    PROGNAME="firmware",
    PROGSUFFIX=".elf"
)

if "BOARD" in env:
    env.Append(
        CCFLAGS=[
            "-mcpu=%s" % env.BoardConfig().get("build.cpu")
        ],
        CPPDEFINES=[
            env.BoardConfig().get("build.variant", "").upper()
        ],
        LINKFLAGS=[
            "-mcpu=%s" % env.BoardConfig().get("build.cpu")
        ]
    )

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".bin"
        ),
        ElfToHex=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "-R",
                ".eeprom",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".hex"
        )
    )
)

if env.subst("$UPLOAD_PROTOCOL") == "gdb":
    if not isfile(join(env.subst("$PROJECT_DIR"), "upload.gdb")):
        env.Exit(
            "Error: You are using GDB as firmware uploader. "
            "Please specify upload commands in upload.gdb "
            "file in project directory!"
        )
    env.Replace(
        UPLOADER="arm-none-eabi-gdb",
        UPLOADERFLAGS=[
            join("$BUILD_DIR", "firmware.elf"),
            "-batch",
            "-x",
            join("$PROJECT_DIR", "upload.gdb")
        ],

        UPLOADCMD='$UPLOADER $UPLOADERFLAGS'
    )

elif env.subst("$UPLOAD_PROTOCOL") in ("serial", "dfu") \
        and "arduino" in env.subst("$PIOFRAMEWORK"):
    _upload_tool = "serial_upload"
    _upload_flags = ["{upload.altID}", "{upload.usbID}"]
    if env.subst("$UPLOAD_PROTOCOL") == "dfu":
        _upload_tool = "maple_upload"
        _usbids = env.BoardConfig().get("build.hwids")
        _upload_flags = [env.BoardConfig().get("upload.boot_version", 2),
                         "%s:%s" % (_usbids[0][0][2:], _usbids[0][1][2:])]

    env.Replace(
        UPLOADER=_upload_tool,
        UPLOADERFLAGS=["$UPLOAD_PORT"] + _upload_flags,
        UPLOADCMD=(
            '$UPLOADER $UPLOADERFLAGS $PROJECT_DIR/$SOURCES'))

#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.bin")
else:
    target_elf = env.BuildProgram()
    target_firm = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)

#
# Target: Print binary size
#

target_size = env.Alias(
    "size", target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

if "mbed" in env.subst("$PIOFRAMEWORK") and not env.subst("$UPLOAD_PROTOCOL"):
    target_upload = env.Alias(
        "upload", target_firm,
        [env.VerboseAction(env.AutodetectUploadPort,
                           "Looking for upload disk..."),
         env.VerboseAction(env.UploadToDisk, "Uploading $SOURCE")])
elif "arduino" in env.subst("$PIOFRAMEWORK") and \
        env.subst("$UPLOAD_PROTOCOL") != "stlink":

    def BeforeUpload(target, source, env):
        env.AutodetectUploadPort()
        env.Replace(UPLOAD_PORT=basename(env.subst("$UPLOAD_PORT")))

    target_upload = env.Alias(
        "upload", target_firm,
        [env.VerboseAction(BeforeUpload,
                           "Looking for upload disk..."),
         env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")])
else:
    target_upload = env.Alias(
        "upload", target_firm,
        env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE"))
AlwaysBuild(target_upload)

#
# Default targets
#

Default([target_buildprog, target_size])
