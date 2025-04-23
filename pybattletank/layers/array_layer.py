from typing import Optional

import pygame

from pybattletank.state.game_state import GameState

from .theme import Theme
from .tiled_layer import TiledLayer


class ArrayLayer(TiledLayer):
    def __init__(
        self,
        theme: Theme,
        image_filename: str,
        state: GameState,
        array: list[list[Optional[tuple[int, int]]]],
        surface_flags: int = pygame.SRCALPHA,
    ) -> None:
        super().__init__(theme, image_filename)
        self.state = state
        self.array = array
        self.surface: Optional[pygame.Surface] = None
        self.surface_flags = surface_flags

    def render(self, surface: pygame.Surface) -> None:
        if self.surface is None:
            self.surface = pygame.Surface(surface.get_size(), self.surface_flags)
            for y in range(self.state.world_size[1]):
                for x in range(self.state.world_size[0]):
                    tile = self.array[y][x]
                    if tile is not None:
                        self.draw_tile(self.surface, (x, y), tile)
        surface.blit(self.surface, (0, 0))
