import json
import os
from typing import Any, Optional, Union

from pybattletank.locators.asset_locator import AssetLocator


class LoadThemeError(RuntimeError):
    def __init__(self, message: str, *args: Any) -> None:
        self.message = message.format(*args)
        super().__init__(self.message)


class Theme:
    def __init__(self, locator: AssetLocator, filename: str) -> None:
        self.locator = locator

        loc = locator.locate(filename)
        with open(loc, encoding="utf-8") as file:
            data = json.load(file)

        def fail_if_not_exists(data: dict[str, dict[str, Any]], section: str, name: str) -> str:
            if section not in data:
                msg = "No section {} in {}"
                raise LoadThemeError(msg, section, filename)
            section_data = data[section]
            if name not in section_data:
                msg = "No section {}.{} in {}"
                raise LoadThemeError(msg, section, name, filename)
            location = locator.locate(section_data[name])
            if not os.path.exists(location):
                msg = "No file {}"
                raise LoadThemeError(msg, location)
            return str(location)

        self.default_window_width = int(data["defaultWindowWidth"])
        self.default_window_height = int(data["defaultWindowHeight"])

        self.title_font = fail_if_not_exists(data, "font", "title")
        self.title_size = int(data["font"]["titleSize"])
        self.menu_font = fail_if_not_exists(data, "font", "menu")
        self.menu_size = int(data["font"]["menuSize"])
        self.message_font = fail_if_not_exists(data, "font", "message")
        self.message_size = int(data["font"]["messageSize"])

        self.cursor_image = fail_if_not_exists(data, "image", "cursor")

        tile_data = data["tile"]
        tile_width = tile_data["width"]
        tile_height = tile_data["height"]
        self.tile_size = (tile_width, tile_height)
        self.ground_tileset = fail_if_not_exists(data, "tile", "ground")
        self.walls_tileset = fail_if_not_exists(data, "tile", "walls")
        self.units_tileset = fail_if_not_exists(data, "tile", "units")
        self.bullets_tileset = fail_if_not_exists(data, "tile", "bullets")
        self.explosions_tileset = fail_if_not_exists(data, "tile", "explosions")

        def set_if_exists(data: dict[str, dict[str, Any]], section: str, name: str) -> Optional[str]:
            if section not in data:
                return None
            section_data = data[section]
            if name not in section_data:
                return None
            location: str = section_data[name]
            return location if not os.path.exists(location) else None

        self.fire_sound = set_if_exists(data, "sound", "fire")
        self.explosion_sound = set_if_exists(data, "sound", "explosion")
        self.start_music = set_if_exists(data, "music", "start")
        self.play_music = set_if_exists(data, "music", "play")
        self.victory_music = set_if_exists(data, "music", "victory")
        self.fail_music = set_if_exists(data, "music", "fail")

    def locate_resource(self, name: str) -> Union[str, os.PathLike]:
        return self.locator.locate(name)
