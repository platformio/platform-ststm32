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
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://www.stm32duino.com
"""

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

# supported mcu types by official STM32 Arduino core
supported = [
    "f030r8", "f091rc",
    "f100rb",
    "f103c", "f103rb",
    "f207zg",
    "f302r8", "f303k8", "f303re",
    "f401re", "f411re", "f429zi", "f446re", "f407vg",
    "f746ng",
    "l031k6", "l053r8", "l072cz",
    "l152re",
    "l432kc", "l476rg", "l496zg", "l475vg"
]

mcu_type = env.BoardConfig().get("build.mcu")
official = False

if not "f103" in mcu_type or not "f407" in mcu_type:
    official = True

if "STM32_OFFICIAL_CORE" in env['CPPDEFINES']:
    for mcu in supported:
        if mcu in mcu_type:
            official = True
            break

if official:
    env.SConscript("stm32core.py")
elif "stm32f1" in env.BoardConfig().get("build.variant"):
    env.SConscript("maple/stm32f1.py")
elif "stm32f4" in env.BoardConfig().get("build.variant"):
    env.SConscript("maple/stm32f4.py")
