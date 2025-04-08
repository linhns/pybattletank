import os

import pygame

from pybattletank.game import UserInterface

os.environ["SDL_VIDEO_CENTERED"] = "1"


async def main() -> None:
    game = UserInterface()
    await game.run()
    pygame.quit()
