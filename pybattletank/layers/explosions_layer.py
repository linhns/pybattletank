import math
from typing import Any

import pygame

from pybattletank.state.unit import Unit

from .theme import Theme
from .tiled_layer import TiledLayer


class ExplosionsLayer(TiledLayer):
    def __init__(self, theme: Theme, image_filename: str) -> None:
        super().__init__(theme, image_filename)
        self.explosions: list[dict[str, Any]] = []
        self.max_frame_index = 27

    def add(self, position: tuple[int, int]) -> None:
        self.explosions.append({"position": position, "frameIndex": 0.0})

    def render(self, surface: pygame.Surface) -> None:
        for explosion in self.explosions:
            frame_index = math.floor(explosion["frameIndex"])
            position = explosion["position"]
            self.draw_tile(surface, position, (frame_index, 4))
            explosion["frameIndex"] += 0.5

        self.explosions = [explosion for explosion in self.explosions if explosion["frameIndex"] < self.max_frame_index]

    def unit_destroyed(self, unit: Unit) -> None:
        self.add(unit.position)
