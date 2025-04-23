import pygame

from pybattletank.state.bullet import Bullet
from pybattletank.state.game_state import GameState

from .theme import Theme
from .tiled_layer import TiledLayer


class BulletsLayer(TiledLayer):
    def __init__(self, theme: Theme, image_filename: str, state: GameState, bullets: list[Bullet]) -> None:
        super().__init__(theme, image_filename)
        self.state = state
        self.bullets = bullets

    def render(self, surface: pygame.Surface) -> None:
        for bullet in self.bullets:
            if bullet.alive:
                self.draw_tile(surface, bullet.position, bullet.tile, bullet.orientation)
