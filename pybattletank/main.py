import os
import sys

import pygame

from pybattletank.finders.directory_level_finder import DirectoryLevelFinder
from pybattletank.finders.level_finder import LevelFinder
from pybattletank.finders.multisource_level_finder import MultiSourceLevelFinder
from pybattletank.finders.packaged_level_finder import PackagedLevelFinder
from pybattletank.layers.theme import Theme
from pybattletank.locators.asset_locator import AssetLocator
from pybattletank.locators.directory_asset_locator import DirectoryAssetLocator
from pybattletank.locators.packaged_asset_locator import PackagedAssetLocator
from pybattletank.ui.user_interface import UserInterface

os.environ["SDL_VIDEO_CENTERED"] = "1"


async def run() -> None:
    locator: AssetLocator
    packaged_level_finder: LevelFinder
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        locator = DirectoryAssetLocator(os.path.join(sys._MEIPASS, "assets"))
        packaged_level_finder = DirectoryLevelFinder(os.path.join(sys._MEIPASS, "assets"))
    else:
        locator = PackagedAssetLocator("pybattletank.assets")
        packaged_level_finder = PackagedLevelFinder("pybattletank.assets")

    theme = Theme(locator, "theme.json")
    current_dir_level_finder = DirectoryLevelFinder("./levels")
    level_finder = MultiSourceLevelFinder(packaged_level_finder, current_dir_level_finder)
    game = UserInterface(theme, locator, level_finder)
    await game.run()
    pygame.quit()
