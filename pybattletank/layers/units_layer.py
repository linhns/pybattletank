import math

import pygame

from pybattletank.state.game_state import GameState
from pybattletank.state.unit import Unit

from .theme import Theme
from .tiled_layer import TiledLayer


class UnitsLayer(TiledLayer):
    def __init__(self, theme: Theme, image_filename: str, state: GameState, units: list[Unit]) -> None:
        super().__init__(theme, image_filename)
        self.state = state
        self.units = units

    def render(self, surface: pygame.Surface) -> None:
        for unit in self.units:
            self.draw_tile(surface, unit.position, unit.tile, unit.orientation)
            if not unit.alive:
                continue

            dir_x = unit.weapon_target[0] - unit.position[0]
            dir_y = unit.weapon_target[1] - unit.position[1]
            angle = math.atan2(-dir_x, -dir_y) * 180 / math.pi

            self.draw_tile(surface, unit.position, (4, 1), angle)
