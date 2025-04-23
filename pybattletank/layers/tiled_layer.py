from typing import Optional

import pygame

from .layer import Layer
from .theme import Theme


class TiledLayer(Layer):
    def __init__(self, theme: Theme, imagefile: str) -> None:
        super().__init__(theme)
        self.tileset = pygame.image.load(imagefile)

    def draw_tile(
        self,
        surface: pygame.Surface,
        position: tuple[int, int],
        tile_coords: tuple[int, int],
        angle: Optional[float] = None,
    ) -> None:
        tile_width = self.theme.tile_size[0]
        tile_height = self.theme.tile_size[1]
        sprite_x = position[0] * tile_width
        sprite_y = position[1] * tile_height
        tile_x = tile_coords[0] * tile_width
        tile_y = tile_coords[1] * tile_height
        tile_rect = pygame.Rect(tile_x, tile_y, tile_width, tile_height)

        if angle is None:
            surface.blit(self.tileset, (sprite_x, sprite_y), tile_rect)
        else:
            tile = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
            tile.blit(self.tileset, (0, 0), tile_rect)
            rotated_tile = pygame.transform.rotate(tile, angle)
            sprite_x -= (rotated_tile.get_width() - tile.get_width()) // 2
            sprite_y -= (rotated_tile.get_height() - tile.get_height()) // 2
            surface.blit(rotated_tile, (sprite_x, sprite_y))
