Import('env')
from os.path import join

global_env = DefaultEnvironment()
global_env.Replace(
    LDSCRIPT_PATH=join("$PROJECTSRC_DIR", "TARGET_STM32L452xE", "device",
                       "TOOLCHAIN_GCC_ARM", "STM32L452XX.ld"))
