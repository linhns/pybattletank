import os

import pygame

from pybattletank.game import UserInterface

os.environ["SDL_VIDEO_CENTERED"] = "1"


def main() -> None:
    game = UserInterface()
    game.run()
    pygame.quit()
