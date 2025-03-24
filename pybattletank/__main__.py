import pygame

from pybattletank.game import Game


def main() -> None:
    game = Game()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
