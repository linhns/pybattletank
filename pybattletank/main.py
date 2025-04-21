import os

import pygame

from pybattletank.game import (
    DirectoryLevelFinder,
    MultiSourceLevelFinder,
    PackagedAssetLocator,
    PackagedLevelFinder,
    Theme,
    UserInterface,
)

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
