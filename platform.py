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

from platformio.managers.platform import PlatformBase


class Ststm32Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        board = variables.get("board")

        if board == "mxchip_az3166":
            self.frameworks['arduino'][
                'package'] = "framework-arduinostm32mxchip"
            self.frameworks['arduino'][
                'script'] = "builder/frameworks/arduino/mxchip.py"

            self.packages['tool-openocd']['type'] = "uploader"

            self.packages['toolchain-gccarmnoneeabi']['version'] = "~1.60301.0"

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
        for link in ("blackmagic", "jlink", "stlink"):
            if link not in upload_protocols or link in debug['tools']:
                continue
            if link == "blackmagic":
                debug['tools']['blackmagic'] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
                continue

            server_args = []
            if link in debug.get("onboard_tools",
                                 []) and debug.get("openocd_board"):
                server_args = [
                    "-f",
                    "scripts/board/%s.cfg" % debug.get("openocd_board")
                ]
            else:
                assert debug.get("openocd_target"), (
                    "Missed target configuration for %s" % board.id)

                server_args = ["-f", "scripts/interface/%s.cfg" % link]
                if link == "stlink":
                    server_args.extend(["-c", "transport select hla_swd"])

                server_args.extend([
                    "-f",
                    "scripts/target/%s.cfg" % debug.get("openocd_target")
                ])

            if debug.get("openocd_extra_args"):
                server_args.extend(debug.get("openocd_extra_args"))

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
