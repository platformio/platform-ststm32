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

import os
import sys
import subprocess

from platformio.managers.platform import PlatformBase


IS_WINDOWS = sys.platform.startswith("win")


class Ststm32Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        board = variables.get("board")
        board_config = self.board_config(board)
        build_core = variables.get(
            "board_build.core", board_config.get("build.core", "arduino"))
        build_mcu = variables.get("board_build.mcu", board_config.get("build.mcu", ""))

        frameworks = variables.get("pioframework", [])
        if "arduino" in frameworks:
            if board.startswith(("portenta", "opta", "nicla_vision", "giga")):
                self.frameworks["arduino"]["package"] = "framework-arduino-mbed"
                self.frameworks["arduino"][
                    "script"
                ] = "builder/frameworks/arduino/mbed-core/arduino-core-mbed.py"
                self.packages["framework-arduinoststm32"]["optional"] = True
            elif build_core == "maple":
                self.frameworks["arduino"]["package"] = "framework-arduinoststm32-maple"
                self.packages["framework-arduinoststm32-maple"]["optional"] = False
                self.packages["framework-arduinoststm32"]["optional"] = True
            elif build_core == "stm32l0":
                self.frameworks["arduino"]["package"] = "framework-arduinoststm32l0"
                self.packages["framework-arduinoststm32l0"]["optional"] = False
                self.packages["framework-arduinoststm32"]["optional"] = True
            else:
                self.packages["toolchain-gccarmnoneeabi"]["version"] = "~1.120301.0"
                self.packages["framework-cmsis"]["version"] = "~2.50900.0"
                self.packages["framework-cmsis"]["optional"] = False

        if "mbed" in frameworks:
            self.packages["toolchain-gccarmnoneeabi"]["version"] = "~1.90201.0"

        if "cmsis" in frameworks:
            assert build_mcu, ("Missing MCU field for %s" % board)
            device_package = "framework-cmsis-" + build_mcu[0:7]
            if device_package in self.packages:
                self.packages[device_package]["optional"] = False

        if "stm32cube" in frameworks:
            assert build_mcu, ("Missing MCU field for %s" % board)
            device_package = "framework-stm32cube%s" % build_mcu[5:7]
            self.frameworks["stm32cube"]["package"] = device_package

        if any(f in frameworks for f in ("cmsis", "stm32cube")):
            self.packages["tool-ldscripts-ststm32"]["optional"] = False

        default_protocol = board_config.get("upload.protocol") or ""
        if variables.get("upload_protocol", default_protocol) == "dfu":
            dfu_package = "tool-dfuutil"
            if board.startswith(("portenta", "opta", "nicla", "giga")):
                dfu_package = "tool-dfuutil-arduino"
                self.packages.pop("tool-dfuutil")
            else:
                self.packages.pop("tool-dfuutil-arduino")
            self.packages[dfu_package]["optional"] = False

        if board == "mxchip_az3166":
            self.frameworks["arduino"][
                "package"] = "framework-arduinostm32mxchip"
            self.frameworks["arduino"][
                "script"] = "builder/frameworks/arduino/mxchip.py"
            self.packages["toolchain-gccarmnoneeabi"]["version"] = "~1.60301.0"

        if "zephyr" in variables.get("pioframework", []):
            for p in self.packages:
                if p in ("tool-cmake", "tool-dtc", "tool-ninja"):
                    self.packages[p]["optional"] = False
            self.packages["toolchain-gccarmnoneeabi"]["version"] = "~1.120301.0"
            if not IS_WINDOWS:
                self.packages["tool-gperf"]["optional"] = False

        # configure J-LINK tool
        jlink_conds = [
            "jlink" in variables.get(option, "")
            for option in ("upload_protocol", "debug_tool")
        ]
        if board:
            jlink_conds.extend([
                "jlink" in board_config.get(key, "")
                for key in ("debug.default_tools", "upload.protocol")
            ])
        jlink_pkgname = "tool-jlink"
        if not any(jlink_conds) and jlink_pkgname in self.packages:
            del self.packages[jlink_pkgname]

        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

    def install_package(self, name, *args, **kwargs):
        pkg = super().install_package(name, *args, **kwargs)
        if name != "framework-zephyr":
            return pkg

        if not os.path.isfile(os.path.join(pkg.path, "_pio", "state.json")):
            self.pm.log.info("Installing Zephyr project dependencies...")
            try:
                subprocess.run([
                    os.path.normpath(sys.executable),
                    os.path.join(pkg.path, "scripts", "platformio", "install-deps.py"),
                    "--platform", self.name
                ])
            except subprocess.CalledProcessError:
                self.pm.log.info("Failed to install Zephyr dependencies!")

        return pkg

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}

        # BlackMagic, J-Link, ST-Link
        for link in ("blackmagic", "jlink", "stlink", "cmsis-dap"):
            if link not in upload_protocols or link in debug["tools"]:
                continue
            if link == "blackmagic":
                debug["tools"]["blackmagic"] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
            elif link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug["tools"][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "SWD",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if IS_WINDOWS else
                                       "JLinkGDBServer")
                    }
                }
            else:
                server_args = ["-s", "$PACKAGE_DIR/openocd/scripts"]
                if debug.get("openocd_board"):
                    server_args.extend([
                        "-f", "board/%s.cfg" % debug.get("openocd_board")
                    ])
                else:
                    assert debug.get("openocd_target"), (
                        "Missed target configuration for %s" % board.id)
                    server_args.extend([
                        "-f", "interface/%s.cfg" % link,
                        "-c", "transport select %s" % (
                            "hla_swd" if link == "stlink" else "swd"),
                        "-f", "target/%s.cfg" % debug.get("openocd_target")
                    ])
                    server_args.extend(debug.get("openocd_extra_args", []))

                debug["tools"][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    }
                }
            debug["tools"][link]["onboard"] = link in debug.get("onboard_tools", [])
            debug["tools"][link]["default"] = link in debug.get("default_tools", [])

        board.manifest["debug"] = debug
        return board

    def configure_debug_session(self, debug_config):
        if debug_config.speed:
            server_executable = (debug_config.server or {}).get("executable", "").lower()
            if "openocd" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-c", "adapter speed %s" % debug_config.speed]
                )
            elif "jlink" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-speed", debug_config.speed]
                )
