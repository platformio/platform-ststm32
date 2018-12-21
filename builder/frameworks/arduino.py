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

from os import listdir
from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
mcu = env.BoardConfig().get("build.mcu")
variant = env.BoardConfig().get("build.variant")

core_variant_dir = join(env.PioPlatform().get_package_dir(
    "framework-arduinoststm32"), "STM32", "variants")

if variant in listdir(core_variant_dir):
    env.SConscript("arduino/stm32duino.py")
else:
    # STM32 legacy core supported families
    if "f1" in mcu:
        env.SConscript("arduino/maple/stm32f1.py")
    elif "f4" in mcu:
        env.SConscript("arduino/maple/stm32f4.py")
    else:
        env.SConscript("arduino/stm32duino.py")
