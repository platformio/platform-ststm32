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

from platform import system

from platformio.managers.platform import PlatformBase


class Ststm32Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        board = variables.get("board")
        build_core = variables.get(
            "board_build.core", self.board_config(variables.get("board")).get(
                "build.core", "arduino"))

        if "arduino" in variables.get("pioframework", []) and build_core == "maple":
            self.frameworks['arduino']['package'] = "framework-arduinoststm32-maple"
            self.packages["framework-arduinoststm32-maple"]["optional"] = False
            self.packages["framework-arduinoststm32"]["optional"] = True

        default_protocol = self.board_config(variables.get(
            "board")).get("upload.protocol") or ""
        if variables.get("upload_protocol", default_protocol) == "dfu":
            self.packages["tool-dfuutil"]["optional"] = False

        if board == "mxchip_az3166":
            self.frameworks['arduino'][
                'package'] = "framework-arduinostm32mxchip"
            self.frameworks['arduino'][
                'script'] = "builder/frameworks/arduino/mxchip.py"
            self.packages['toolchain-gccarmnoneeabi']['version'] = "~1.60301.0"

        # configure J-LINK tool
        jlink_conds = [
            "jlink" in variables.get(option, "")
            for option in ("upload_protocol", "debug_tool")
        ]
        if variables.get("board"):
            board_config = self.board_config(variables.get("board"))
            jlink_conds.extend([
                "jlink" in board_config.get(key, "")
                for key in ("debug.default_tools", "upload.protocol")
            ])
        jlink_pkgname = "tool-jlink"
        if not any(jlink_conds) and jlink_pkgname in self.packages:
            del self.packages[jlink_pkgname]

        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

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
            debug['tools'] = {}

        # BlackMagic, J-Link, ST-Link
        for link in ("blackmagic", "jlink", "stlink", "cmsis-dap"):
            if link not in upload_protocols or link in debug['tools']:
                continue
            if link == "blackmagic":
                debug['tools']['blackmagic'] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
            elif link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug['tools'][link] = {
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
                                       if system() == "Windows" else
                                       "JLinkGDBServer")
                    },
                    "onboard": link in debug.get("onboard_tools", [])
                }
            else:
                server_args = ["-s", "$PACKAGE_DIR/scripts"]
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

                debug['tools'][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    },
                    "onboard": link in debug.get("onboard_tools", []),
                    "default": link in debug.get("default_tools", [])
                }

        board.manifest['debug'] = debug
        return board
