import os
from typing import Optional

import tmx

from .game_state import GameState
from .unit import Unit


class LoadLevelError(RuntimeError):
    def __init__(self, filename: str, message: str):
        super().__init__(f"{filename}: {message}")
        self.filename = filename
        self.message = message


class LevelLoader:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.state = GameState()

    def decode_layer_header(self, tilemap: tmx.TileMap, layer: tmx.Layer) -> tmx.Tileset:
        if not isinstance(layer, tmx.Layer):
            raise LoadLevelError(self.filename, "invalid layer type")
        if len(layer.tiles) != tilemap.width * tilemap.height:
            raise LoadLevelError(self.filename, "invalid tiles count")

        tiles: list[tmx.LayerTile] = layer.tiles
        gid = next((tile.gid for tile in tiles if tile.gid != 0), None)

        if gid is None:
            if len(tilemap.tilesets) == 0:
                raise LoadLevelError(self.filename, "no tilesets")
            tileset = tilemap.tilesets[0]
        else:
            tileset = next(
                (t for t in tilemap.tilesets if gid >= t.firstgid and gid < t.firstgid + t.tilecount),
                None,
            )
            if tileset is None:
                raise LoadLevelError(self.filename, "no corresponding tileset")

        if tileset.columns <= 0:
            raise LoadLevelError(self.filename, "invalid columns count")
        if tileset.image.data is not None:
            raise LoadLevelError(self.filename, "embedded tileset image is not supported")

        return tileset

    def decode_array_layer(
        self, tilemap: tmx.TileMap, layer: tmx.Layer
    ) -> tuple[tmx.Tileset, list[list[Optional[tuple[int, int]]]]]:
        tileset = self.decode_layer_header(tilemap, layer)

        array: list[list[Optional[tuple[int, int]]]] = [
            [None for _ in range(tilemap.width)] for _ in range(tilemap.height)
        ]

        for y in range(tilemap.height):
            for x in range(tilemap.width):
                tile = layer.tiles[x + y * tilemap.width]
                if tile.gid == 0:
                    continue
                lid = tile.gid - tileset.firstgid
                if lid < 0 or lid >= tileset.tilecount:
                    raise LoadLevelError(self.filename, "invalid tile id")

                tile_x = lid % tileset.columns
                tile_y = lid // tileset.columns
                array[y][x] = (tile_x, tile_y)

        return tileset, array

    def decode_units_layer(
        self, state: GameState, tilemap: tmx.TileMap, layer: tmx.Layer
    ) -> tuple[tmx.Tileset, list[Unit]]:
        tileset = self.decode_layer_header(tilemap, layer)

        units = []

        for y in range(tilemap.height):
            for x in range(tilemap.width):
                tile = layer.tiles[x + y * tilemap.width]
                if tile.gid == 0:
                    continue
                lid = tile.gid - tileset.firstgid
                if lid < 0 or lid >= tileset.tilecount:
                    raise LoadLevelError(self.filename, "invalid tile id")

                tile_x = lid % tileset.columns
                tile_y = lid // tileset.columns
                unit = Unit((x, y), (tile_x, tile_y))
                units.append(unit)

        return tileset, units

    def run(self) -> None:
        if not os.path.exists(self.filename):
            raise LoadLevelError(self.filename, "file not exist")

        tilemap = tmx.TileMap.load(self.filename)
        if tilemap.orientation != "orthogonal":
            raise LoadLevelError(self.filename, "invalid orientation")

        if len(tilemap.layers) != 5:
            raise LoadLevelError(self.filename, "expected 5 layers")

        self.state = state = GameState()
        state.world_size = (tilemap.width, tilemap.height)

        tileset, array = self.decode_array_layer(tilemap, tilemap.layers[0])
        self.tile_size = tile_size = (tileset.tilewidth, tileset.tileheight)
        state.ground[:] = array
        self.ground_tileset = tileset.image.source

        tileset, array = self.decode_array_layer(tilemap, tilemap.layers[1])
        if tileset.tilewidth != tile_size[0] or tileset.tileheight != tile_size[1]:
            raise LoadLevelError(self.filename, "tile size must be consistent for all layers")
        state.walls[:] = array
        self.walls_tileset = tileset.image.source

        tanks_tileset, tanks = self.decode_units_layer(state, tilemap, tilemap.layers[2])
        towers_tileset, towers = self.decode_units_layer(state, tilemap, tilemap.layers[3])
        if tanks_tileset != towers_tileset:
            raise LoadLevelError(self.filename, "tanks and towers tilesets must be the same")
        if tanks_tileset.tilewidth != tile_size[0] or tanks_tileset.tileheight != tile_size[1]:
            raise LoadLevelError(self.filename, "tile size must be consistent for all layers")
        state.units = tanks + towers
        self.units_tileset = tanks_tileset.image.source

        tileset, array = self.decode_array_layer(tilemap, tilemap.layers[4])
        if tileset.tilewidth != tile_size[0] or tileset.tileheight != tile_size[1]:
            raise LoadLevelError(self.filename, "tile size must be consistent for all layers")
        self.bullets_tileset = tileset.image.source
        self.explosions_tileset = tileset.image.source
