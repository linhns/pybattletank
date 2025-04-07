import importlib.resources
import os

import pygame

from pybattletank.game import UserInterface

os.environ["SDL_VIDEO_CENTERED"] = "1"


def main() -> None:
    level_path = importlib.resources.files("pybattletank.assets").joinpath("level1.tmx")
    game = UserInterface(str(level_path))
    game.run()
    pygame.quit()
