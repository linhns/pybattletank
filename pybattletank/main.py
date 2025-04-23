import os

import pygame

from pybattletank.finders.directory_level_finder import DirectoryLevelFinder
from pybattletank.finders.multisource_level_finder import MultiSourceLevelFinder
from pybattletank.finders.packaged_level_finder import PackagedLevelFinder
from pybattletank.layers.theme import Theme
from pybattletank.locators.packaged_asset_locator import PackagedAssetLocator
from pybattletank.ui.user_interface import UserInterface

os.environ["SDL_VIDEO_CENTERED"] = "1"


async def main() -> None:
    locator = PackagedAssetLocator("pybattletank.assets")
    theme = Theme(locator, "theme.json")
    packaged_level_finder = PackagedLevelFinder("pybattletank.assets")
    current_dir_level_finder = DirectoryLevelFinder("./levels")
    level_finder = MultiSourceLevelFinder(packaged_level_finder, current_dir_level_finder)
    game = UserInterface(theme, locator, level_finder)
    await game.run()
    pygame.quit()
