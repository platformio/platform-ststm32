"""
Chibios 18.2.1

Repository: https://github.com/ChibiOS/ChibiOS.git
Branch: stable_18.2.x

ChibiOS is a complete development environment for embedded applications 
including RTOS, an HAL, peripheral drivers, support files and tools.

http://www.chibios.org
"""

################################################################################
# Imports
################################################################################
from glob import glob
from os import listdir, walk
from os.path import basename, isdir, isfile, join, abspath
from shutil import copy
from string import Template
import sys
import os
import json
import re

from SCons.Script import DefaultEnvironment


env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = join(platform.get_package_dir("framework-chibios"),"os")
ROOT = abspath(join(FRAMEWORK_DIR, ".."))
PLATFORMS = abspath(join(ROOT, "..", "..", "platforms"))
assert isdir(FRAMEWORK_DIR)

FRAMEWORK_CORE = env.BoardConfig().get("build.mcu")[5:7].lower()
MCU_FAMILY = env.BoardConfig().get("build.mcu")[0:7]
MCU_PORT = MCU_FAMILY.upper() + "xx"
BOARD = env.get("BOARD")
COMPILER = "GCC"
STSTM32_PORTS = [
    "STM32F0xx",
    "STM32F1xx",
    "STM32F2xx",
    "STM32F3xx",
    "STM32F4xx",
    "STM32F7xx",
    "STM32H7xx",
    "STM32L0xx",
    "STM32L1xx",
    "STM32L4xx"
]

print(env.__dict__)

def log_message(msg):
    print(msg)

log_message("MCU family: %s" % MCU_FAMILY)

cpp_flags = env.Flatten(env.get("CPPDEFINES", []))

# Define RTOS usage
if "PIO_CHIBIOS_USE_NIL" in cpp_flags:
    OSAL = "nil"
    OSAL_PATH = join(FRAMEWORK_DIR, "hal", "osal", "nil")

elif "PIO_CHIBIOS_USE_RT" in cpp_flags:
    OSAL = "rt"
    OSAL_PATH = join(FRAMEWORK_DIR, "hal", "osal", "rt")

else:
    OSAL = "os-less"
    OSAL_PATH = join(FRAMEWORK_DIR, "hal", "osal", "os-less", "ARMCMx")

# Define v6m or v7m
if MCU_FAMILY.lower() in ["f0","l0"]:
    ARM_VERSION = "v6m"
else:
    ARM_VERSION = "v7m"

# Define I2C usage
if "PIO_CHIBIOS_I2C_FALLBACK" in cpp_flags:
    I2CFALLBACK = 1
else:
    I2CFALLBACK = 0

# DEFINE MAIN_STACK_SIZE
MAIN_STACK_SIZE = '0x400'
if "USE_MAIN_STACKSIZE" in cpp_flags:
    index = cpp_flags.index("USE_MAIN_STACKSIZE")+1
    MAIN_STACK_SIZE = cpp_flags[index]
# DEFINE PROCESS_STACK_SIZE
PROCESS_STACK_SIZE = '0x400'
if "USE_PROCESS_STACKSIZE" in cpp_flags:
    index = cpp_flags.index("USE_PROCESS_STACKSIZE")+1
    PROCESS_STACK_SIZE = cpp_flags[index]

log_message("MAIN_STACK_SIZE=%s" % MAIN_STACK_SIZE)
log_message("PROCESS_STACK_SIZE=%s" % PROCESS_STACK_SIZE)

################################################################################
# Board mapping
# These methods generates a json file in the framework directory, containing
# a key-value map between CHIBIOS board names and PIO board names
################################################################################
def check_pio_board_existence(boardName):
    boardFile = join(PLATFORMS, "ststm32", "boards", boardName + ".json")
    return isfile(boardFile)

def generate_pio_to_chibios_variant_map():
    # Get the list of boards supported by the HAL and PIO for STM32
    map = {}
    variants = listdir(join(FRAMEWORK_DIR, "hal", "boards"))

    for variant in variants:
        #log_message("Current Variant %s" % variant)
        
        # NUCLEO boards
        if "NUCLEO" in variant:
            pioBoardName = "nucleo_" +  variant[-6:].lower()
            if check_pio_board_existence(pioBoardName):
                map[pioBoardName] = variant

        # DISCOVERY boards
        if "DISCOVERY" in variant:
            mcu = variant.replace("ST_STM32", "").replace("_DISCOVERY", "").lower()
            if len(mcu) == 5:
                for letter in ["a","c","n","r","v","z"]:
                    pioBoardName = "disco_" + mcu[0:4] + letter + mcu[4]
                    if check_pio_board_existence(pioBoardName):
                        map[pioBoardName] = variant
                        break
    with open(join(ROOT, "platformio", "pio_to_chibios_variants.json"), 'w') as fp:
        json.dump(map, fp, sort_keys=True, indent=4)
    
    return map

TARGETS = generate_pio_to_chibios_variant_map()
log_message("PIO Board: " + BOARD + " => CHIBIOS Board: " + TARGETS[BOARD])

################################################################################
# Resource Scanners
################################################################################
def get_config_files():
    # Find the include path(s) for the config files:
    # chconf.h, mcuconf.h, halconf.h, osalconf.h
    srcDir = join(env.get("PROJECTSRC_DIR"))

    configPaths = []
    for root, dirs, files in os.walk(srcDir):
        for file in files:
            if file in ["chconf.h","mcuconf.h","halconf.h","osalconf.h"]:
                configPaths.append(os.path.join(root))

    return list(set(configPaths))

def get_linker_script(mcu):
    # Find the linker script and if it has includes then create a merged script
    ldscript = join(FRAMEWORK_DIR, "common", "startup", "ARMCMx", "compilers", COMPILER, "ld", mcu[0:9].upper() + "x" + mcu[10].upper() + ".ld")

    if not isfile(ldscript):
        log_message("Warning! Cannot find a linker script for the required board!")

    # Check for INCLUDED ldscripts
    merged_ldscript = join(ROOT, "platformio", "ldscripts", mcu[0:9].upper() + "x" + mcu[10].upper() + "_MERGED.ld")

    def _include_callback(match):
        included_ld_file = match.group(1)
        # search included ld file in  directory
        for root, _, files in walk(join(FRAMEWORK_DIR, "common", "startup", "ARMCMx", "compilers", COMPILER, "ld")):
            if included_ld_file not in files:
                continue
            with open(join(root, included_ld_file)) as f:
                return f.read()
        return match.group(0)

    # Save the content of the main linker file to content
    with open(ldscript) as f:
        content = f.read()
    
    with open(merged_ldscript, "w") as f:
        f.write("")
        f.write(content)

    # Append the included linker scripts to the end of content
    includeRegex = re.compile(r"^INCLUDE\s+\"?([^\.]+\.ld)\"?", re.M)

    while (1):
        with open(merged_ldscript) as f:
            content = f.read()

        if (len(includeRegex.findall(content)) == 0):
            break

        with open(merged_ldscript, "w") as f:
            f.write(includeRegex.sub(_include_callback, content))
    
    return merged_ldscript

def parse_makefile(makefile, prefix, type):
    # Parse a makefile looking for specific type=[INC|SRC|ASM] and 
    # add thes to a list
    re_sources = re.compile(r"^"+prefix+type+"[\s\S]*?^\s*$", re.MULTILINE)
        
    _sources = []
    with open(makefile) as mkf:
        match = re.search(re_sources, mkf.read())

    if not match:
        # We didn't find anything that matched the regex - exit
        return []

    for line in match.group(0).splitlines():
        # Parse every line in the matched regex
        line = line.replace("\\","").strip()

        if (line.startswith("ifneq") | line.startswith("else") | line.startswith("endif")):
            continue
        if line == "":
            break

        segments = line.split("/")
        path = ""

        if len(segments) >= 3:
            for x in range(2, len(segments)):
                path = join(path, segments[x])
        
        _sources.append(join(FRAMEWORK_DIR, path))
    # Return a sorted unique list
    return list(sorted(set(_sources)))

def get_all_includes():
    # Iterate over all the makefiles specifed in "makefiles" to get
    # all include directories
    _all_includes = []
    for file in makefiles:
        _all_includes = _all_includes + parse_makefile(join(file["Path"], file["Name"]), file["MkPrefix"], "INC")
        
    return _all_includes

def get_all_sources():
    # Iterate over all the makefiles specified in "makefiles" to get
    # all source files
    _all_sources = []
    for file in makefiles:
        _all_sources = _all_sources + parse_makefile(join(file["Path"], file["Name"]), file["MkPrefix"], "SRC")
        _all_sources = _all_sources + parse_makefile(join(file["Path"], file["Name"]), file["MkPrefix"], "ASM")

    return _all_sources

def get_all_srcFilter():
    # Create a source filter for the BuildLibrary method
    srcFilter = ""
    for src in get_all_sources():
        if src.replace(FRAMEWORK_DIR, "") == "\\":
            continue
        srcFilter = srcFilter + " +<" + src.replace(FRAMEWORK_DIR, "").replace("\\","/")[1:] + ">"

    return srcFilter

def get_platform_lld_drivers():
    # Special makefile
    # Find all the included LLD drivers from the platform.mk file
    platformFile = join(FRAMEWORK_DIR, "hal", "ports", "STM32", MCU_PORT, "platform.mk")

    re_includeMk = re.compile(r"^include[\s\S]*(?=[\r\n]{2,})", re.MULTILINE)
    drivers = []

    with open(platformFile) as mkf:
        match = re.search(re_includeMk, mkf.read())

    if not match:
        log_message("Error: No driver.mk files found")

    for line in match.group(0).splitlines():
        if "I2C" in line and I2CFALLBACK == 1:
            drivers.append(join(FRAMEWORK_DIR, "hal", "lib", "fallback", "I2C"))
            # go to next line
            continue
        
        path = line.split("/")
        drivers.append(join(FRAMEWORK_DIR, path[2], path[3], path[4], path[5], path[6]))
        
    return drivers

def get_lld_drivers_srcFilter():
    # Special makefile
    # Create a source filter for all LLD drives included in platform.mk
    lld_src_filter = ""
    for lld in get_platform_lld_drivers():
        if "I2C" in lld and I2CFALLBACK == 1:
            lld = join(FRAMEWORK_DIR, "hal", "lib", "fallback", "I2C", "hal_i2c_lld.c")
        
        lld_src_filter = lld_src_filter + " +<" + lld.replace(FRAMEWORK_DIR, "").replace("\\", "/")[1:] + ">"

    return lld_src_filter

################################################################################
# Compiler and Linker Configuration
################################################################################

# LINKER SCRIPT
ldscript = get_linker_script(env.BoardConfig().get("build.mcu"))
log_message("LD: " + ldscript)

env.Replace(
    AS="$CC",
    ASCOM="$ASPPCOM",
    LDSCRIPT_PATH=ldscript
)

env.Append(
    LIBPATH=[
        join(FRAMEWORK_DIR, "platformio", "ldscripts")
    ]
)

# Compiler Configuration

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-ggdb",
        "-fomit-frame-pointer",
        "-falign-functions=16",
        "-O2",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-fno-common",
        "-Wall",
        "-Wextra",
        "-Wundef",
        "-Wstrict-prototypes",
        #"-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
        "-nostdlib",
        "-Wp,-w"
    ],

    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU")
    ],

    CXXFLAGS=[
        "-fno-exceptions"
    ],

    LINKFLAGS=[
        "-O2",
        "-Wl,--gc-sections,--relax",
        #"-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
        "--specs=nano.specs",
        "--specs=nosys.specs",
        "-Wl,--defsym=__main_stack_size__=%s" % MAIN_STACK_SIZE,
        "-Wl,--defsym=__process_stack_size__=%s" % PROCESS_STACK_SIZE
    ],

    LIBS=["c", "gcc", "m", "stdc++", "nosys"]
)

# FPU Configuration
if "PIO_CHIBIOS_USE_FPU" in cpp_flags:
    env.Append(
        CPPDEFINES=[
            ("CORTEX_USE_FPU","TRUE"),
            ("__FPU_PRESENT", 1),
        ],

        CCFLAGS=[
            "-mfloat-abi=softfp",
            "-mfpu=fpv4-sp-d16",
            "-fsingle-precision-constant"
        ],
    )
else:
    env.Append(
        CPPDEFINES=[
            ("CORTEX_USE_FPU","FALSE"),
            ("__FPU_PRESENT", 0),
        ],
    )

if "PIO_CHIBIOS_USE_CPP" in cpp_flags:
    env.Append(
        CXXFLAGS=[
            "-fno-rtti"
        ]
    )

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

libs = []

################################################################################
# Primary Makefiles
################################################################################
makefiles = [
    #Licensing files
    { 
        "Name": "license.mk", 
        "MkPrefix": "LIC", 
        "Path": join(FRAMEWORK_DIR, "license")
    },
    #Startup files - INC, SRC, ASM, LD
    {
        "Name": "startup_" + MCU_PORT.lower() + ".mk",
        "MkPrefix": "STARTUP",
        "Path": join(FRAMEWORK_DIR, "common", "startup", "ARMCMx", "compilers", COMPILER, "mk")
    },
    # HAL-OSAL_files
    {
        "Name": "hal.mk",
        "MkPrefix": "HAL",
        "Path": join(FRAMEWORK_DIR, "hal")
    },
    {
        "Name": "platform.mk",
        "MkPrefix": "PLATFORM",
        "Path": join(FRAMEWORK_DIR, "hal", "ports", "STM32", MCU_PORT)
    },
    {
        "Name": "board.mk",
        "MkPrefix": "BOARD",
        "Path": join(FRAMEWORK_DIR, "hal", "boards", TARGETS[BOARD])
    },
    {
        "Name": "osal.mk",
        "MkPrefix": "OSAL",
        "Path": OSAL_PATH
    },
    {
        "Name": "streams.mk",
        "MkPrefix": "STREAMS",
        "Path": join(FRAMEWORK_DIR, "hal", "lib", "streams")
    }
]
# RTOS files (optional)
if OSAL in ["rt","nil"]:
    makefiles.append(
        {
            "Name": OSAL+".mk",
            "MkPrefix": "KERN",
            "Path": join(FRAMEWORK_DIR, OSAL)
        }
    )
    makefiles.append(
        {
            "Name": "port_" + ARM_VERSION + ".mk",
            "MkPrefix": "PORT",
            "Path": join(FRAMEWORK_DIR, "common", "ports", "ARMCMx", "compilers", COMPILER, "MK")
        }
    )
# CPP_WRAPPER (optional)
if "PIO_CHIBIOS_USE_CPP" in cpp_flags:
    makefiles.append(
        {
            "Name": "chcpp.mk",
            "MkPrefix": "CHCPP",
            "Path": join(FRAMEWORK_DIR, "various", "cpp_wrappers")
        }
    )
# Other files (optional)
if "PIO_CHIBIOS_USE_TEST" in cpp_flags:
    makefiles.append(
        {
            "Name": "test.mk",
            "MkPrefix": "TEST",
            "Path": join(ROOT, "test", "lib")
        }
    )
    makefiles.append(
        {
            "Name": OSAL + "_test.mk",
            "MkPrefix": "",
            "Path": join(ROOT, "test", OSAL)
        }
    )
    makefiles.append(
        {
            "Name": "oslib_test.mk",
            "MkPrefix": "",
            "Path": join(ROOT, "test", "oslib")
        }
    )


################################################################################
# Parse all makefiles
################################################################################
# INCLUDES
env.Append(
    CPPPATH=get_config_files() + get_all_includes() + get_platform_lld_drivers()
)

# SOURCES
srcfilter = " -<*>" + get_all_srcFilter() + get_lld_drivers_srcFilter()

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkChibios"),
    join(FRAMEWORK_DIR),
    src_filter = srcfilter
))


env.Append(LIBS=libs)