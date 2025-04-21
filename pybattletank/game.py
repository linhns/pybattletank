import asyncio
import importlib.resources
import json
import math
import os
import pathlib
from collections.abc import Sequence
from importlib.resources import Package
from typing import Any, Optional, Union

import pygame
import tmx


class GameItem:
    def __init__(self, state: "GameState", position: tuple[int, int], tile: tuple[int, int]) -> None:
        self.state = state
        self.alive = True
        self.position = position
        self.tile = tile
        self.orientation = 0.0


class Unit(GameItem):
    def __init__(self, state: "GameState", position: tuple[int, int], tile: tuple[int, int]) -> None:
        super().__init__(state, position, tile)
        self.weapon_target = (0.0, 0.0)
        self.last_bullet_epoch = -100


class Bullet(GameItem):
    def __init__(self, state: "GameState", unit: Unit) -> None:
        super().__init__(state, unit.position, (2, 1))
        self.unit = unit
        self.start_position = unit.position
        self.end_position = unit.weapon_target


class IGameStateObserver:
    def unit_destroyed(self, unit: Unit) -> None:
        pass

    def bullet_fired(self, unit: Unit) -> None:
        pass


class GameState:
    def __init__(self) -> None:
        self.world_size = (16, 10)
        self.ground: list[list[Optional[tuple[int, int]]]] = []
        self.walls: list[list[Optional[tuple[int, int]]]] = []
        self.units: list[Unit] = []
        self.bullets: list[Bullet] = []
        self.bullet_speed = 0.1
        self.bullet_range = 4
        self.bullet_delay = 10
        self.epoch = 0
        self.observers: list[IGameStateObserver] = []

    def is_inside(self, position: tuple[float, float]) -> bool:
        return (
            position[0] >= 0
            and position[0] < self.world_size[0]
            and position[1] >= 0
            and position[1] < self.world_size[1]
        )

    def find_unit(self, position: tuple[float, float]) -> Optional[Unit]:
        for unit in self.units:
            if int(unit.position[0]) == int(position[0]) and int(unit.position[1]) == int(position[1]):
                return unit
        return None

    def find_live_unit(self, position: tuple[float, float]) -> Optional[Unit]:
        unit = self.find_unit(position)
        if unit is None or not unit.alive:
            return None
        return unit

    def add_observer(self, observer: IGameStateObserver) -> None:
        self.observers.append(observer)

    def notify_unit_destroyed(self, unit: Unit) -> None:
        for observer in self.observers:
            observer.unit_destroyed(unit)

    def notify_bullet_fired(self, unit: Unit) -> None:
        for observer in self.observers:
            observer.bullet_fired(unit)


class Command:
    def run(self) -> None:
        raise NotImplementedError()


class TargetCommand(Command):
    def __init__(self, state: GameState, unit: Unit, target: tuple[float, float]) -> None:
        self.state = state
        self.unit = unit
        self.target = target

    def run(self) -> None:
        self.unit.weapon_target = self.target


class MoveCommand(Command):
    def __init__(self, state: GameState, unit: Unit, move_vector: tuple[int, int]) -> None:
        self.state = state
        self.unit = unit
        self.move_vector = move_vector

    def run(self) -> None:
        if not self.unit.alive:
            return

        dx, dy = self.move_vector
        if dx < 0:
            self.unit.orientation = 90
        if dx > 0:
            self.unit.orientation = -90
        if dy < 0:
            self.unit.orientation = 0
        if dy < 0:
            self.unit.orientation = 180

        x, y = self.unit.position
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= self.state.world_size[0] or ny < 0 or ny >= self.state.world_size[1]:
            return
        if self.state.walls[ny][nx] is not None:
            return
        for unit in self.state.units:
            if (nx, ny) == unit.position:
                return
        self.unit.position = (nx, ny)


class ShootCommand(Command):
    def __init__(self, state: GameState, unit: Unit) -> None:
        self.state = state
        self.unit = unit

    def run(self) -> None:
        unit = self.unit
        if not unit.alive:
            return

        state = self.state
        if state.epoch - unit.last_bullet_epoch < state.bullet_delay:
            return

        unit.last_bullet_epoch = state.epoch
        state.bullets.append(Bullet(state, unit))


def vector_sub(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return a[0] - b[0], a[1] - b[1]


def vector_add(a: tuple[float, float], b: tuple[float, float], w: float = 1.0) -> tuple[float, float]:
    return a[0] + b[0] * w, a[1] + b[1] * w


def vector_norm(a: tuple[float, float]) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2)


def vector_normalize(a: tuple[float, float]) -> tuple[float, float]:
    norm = vector_norm(a)
    if norm < 1e-4:
        return 0, 0
    return a[0] / norm, a[1] / norm


def vector_dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return vector_norm(vector_sub(a, b))


class MoveBulletCommand(Command):
    def __init__(self, state: GameState, bullet: Bullet) -> None:
        self.state = state
        self.bullet = bullet

    def run(self) -> None:
        bullet = self.bullet
        state = self.state
        direction = vector_sub(bullet.end_position, bullet.start_position)
        direction = vector_normalize(direction)
        new_pos = vector_add(bullet.position, direction, state.bullet_speed)

        if not state.is_inside(new_pos):
            bullet.alive = False
            return

        dir_x, dir_y = direction
        if (
            (dir_x >= 0 and new_pos[0] >= bullet.end_position[0])
            or (dir_x < 0 and new_pos[0] <= bullet.end_position[0])
        ) and (
            (dir_y >= 0 and new_pos[1] >= bullet.end_position[1])
            or (dir_y < 0 and new_pos[1] <= bullet.end_position[1])
        ):
            bullet.alive = False
            return

        if vector_dist(new_pos, bullet.start_position) > state.bullet_range:
            bullet.alive = False
            return

        new_center_pos = vector_add(new_pos, (0.5, 0.5))
        unit = state.find_live_unit(new_center_pos)
        if unit is not None and unit != bullet.unit:
            bullet.alive = False
            unit.alive = False
            state.notify_unit_destroyed(unit)
            return

        bullet.position = new_pos  # type: ignore[assignment]


class DeleteDestroyedCommand(Command):
    def __init__(self, items: Sequence[GameItem]) -> None:
        self.items = items

    def run(self) -> None:
        self.items = [item for item in self.items if item.alive]


class AssetLocator:
    def locate(self, name: str) -> Union[str, os.PathLike]:
        raise NotImplementedError()


class PackagedAssetLocator(AssetLocator):
    def __init__(self, anchor: Package) -> None:
        self.traversable = importlib.resources.files(anchor)

    def locate(self, name: str) -> Union[str, os.PathLike]:
        with importlib.resources.as_file(self.traversable.joinpath(name)) as path:
            fp = path.resolve()
        return fp


class LoadThemeError(RuntimeError):
    def __init__(self, message: str, *args: Any) -> None:
        self.message = message.format(*args)
        super().__init__(self.message)


class Theme:
    def __init__(self, locator: AssetLocator, filename: str) -> None:
        self.locator = locator

        loc = locator.locate(filename)
        with open(loc, encoding="utf-8") as file:
            data = json.load(file)

        def fail_if_not_exists(data: dict[str, dict[str, Any]], section: str, name: str) -> str:
            if section not in data:
                msg = "No section {} in {}"
                raise LoadThemeError(msg, section, filename)
            section_data = data[section]
            if name not in section_data:
                msg = "No section {}.{} in {}"
                raise LoadThemeError(msg, section, name, filename)
            location = locator.locate(section_data[name])
            if not os.path.exists(location):
                msg = "No file {}"
                raise LoadThemeError(msg, location)
            return str(location)

        self.default_window_width = int(data["defaultWindowWidth"])
        self.default_window_height = int(data["defaultWindowHeight"])

        self.title_font = fail_if_not_exists(data, "font", "title")
        self.title_size = int(data["font"]["titleSize"])
        self.menu_font = fail_if_not_exists(data, "font", "menu")
        self.menu_size = int(data["font"]["menuSize"])
        self.message_font = fail_if_not_exists(data, "font", "message")
        self.message_size = int(data["font"]["messageSize"])

        self.cursor_image = fail_if_not_exists(data, "image", "cursor")

        tile_data = data["tile"]
        tile_width = tile_data["width"]
        tile_height = tile_data["height"]
        self.tile_size = (tile_width, tile_height)
        self.ground_tileset = fail_if_not_exists(data, "tile", "ground")
        self.walls_tileset = fail_if_not_exists(data, "tile", "walls")
        self.units_tileset = fail_if_not_exists(data, "tile", "units")
        self.bullets_tileset = fail_if_not_exists(data, "tile", "bullets")
        self.explosions_tileset = fail_if_not_exists(data, "tile", "explosions")

        def set_if_exists(data: dict[str, dict[str, Any]], section: str, name: str) -> Optional[str]:
            if section not in data:
                return None
            section_data = data[section]
            if name not in section_data:
                return None
            location: str = section_data[name]
            return location if not os.path.exists(location) else None

        self.fire_sound = set_if_exists(data, "sound", "fire")
        self.explosion_sound = set_if_exists(data, "sound", "explosion")
        self.start_music = set_if_exists(data, "music", "start")
        self.play_music = set_if_exists(data, "music", "play")
        self.victory_music = set_if_exists(data, "music", "victory")
        self.fail_music = set_if_exists(data, "music", "fail")

    def locate_resource(self, name: str) -> Union[str, os.PathLike]:
        return self.locator.locate(name)


class Layer(IGameStateObserver):
    def __init__(self, theme: Theme) -> None:
        self.theme = theme

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError()


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


class UnitsLayer(TiledLayer):
    def __init__(self, theme: Theme, image_filename: str, state: GameState, units: list[Unit]) -> None:
        super().__init__(theme, image_filename)
        self.state = state
        self.units = units

    def render(self, surface: pygame.Surface) -> None:
        for unit in self.units:
            self.draw_tile(surface, unit.position, unit.tile, unit.orientation)

            dir_x = unit.weapon_target[0] - unit.position[0]
            dir_y = unit.weapon_target[1] - unit.position[1]
            angle = math.atan2(-dir_x, -dir_y) * 180 / math.pi

            self.draw_tile(surface, unit.position, (4, 1), angle)


class BulletsLayer(TiledLayer):
    def __init__(self, theme: Theme, image_filename: str, state: GameState, bullets: list[Bullet]) -> None:
        super().__init__(theme, image_filename)
        self.state = state
        self.bullets = bullets

    def render(self, surface: pygame.Surface) -> None:
        for bullet in self.bullets:
            if bullet.alive:
                self.draw_tile(surface, bullet.position, bullet.tile, bullet.orientation)


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


class SoundLayer(Layer):
    def __init__(self, theme: Theme) -> None:
        super().__init__(theme)
        self.fire_sound: Optional[pygame.mixer.Sound] = None
        self.explosion_sound: Optional[pygame.mixer.Sound] = None

        if theme.fire_sound is not None:
            fire_sound_path = theme.locate_resource(theme.fire_sound)
            self.fire_sound = pygame.mixer.Sound(fire_sound_path)
            self.fire_sound.set_volume(0.2)

        if theme.explosion_sound is not None:
            explosion_sound_path = theme.locate_resource(theme.explosion_sound)
            self.explosion_sound = pygame.mixer.Sound(explosion_sound_path)
            self.explosion_sound.set_volume(0.2)

    def render(self, surface: pygame.Surface) -> None:
        pass

    def unit_destroyed(self, unit: Unit) -> None:
        if self.explosion_sound is not None:
            self.explosion_sound.play()

    def bullets_fired(self, unit: Unit) -> None:
        if self.fire_sound is not None:
            self.fire_sound.play()


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
                unit = Unit(state, (x, y), (tile_x, tile_y))
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


class IGameModeObserver:
    def load_level_requested(self, filename: str) -> None:
        pass

    def show_menu_requested(self, menu_name: str) -> None:
        pass

    def show_message_requested(self, message: str) -> None:
        pass

    def change_theme_requested(self, theme_file: str) -> None:
        pass

    def show_game_requested(self) -> None:
        pass

    def game_won(self) -> None:
        pass

    def game_lost(self) -> None:
        pass

    def quit_requested(self) -> None:
        pass


class GameMode:
    def __init__(self) -> None:
        self.observers: list[IGameModeObserver] = []

    def add_observer(self, observer: IGameModeObserver) -> None:
        self.observers.append(observer)

    def notify_load_level_requested(self, filename: str) -> None:
        for observer in self.observers:
            observer.load_level_requested(filename)

    def notify_show_menu_requested(self, menu_name: str) -> None:
        for observer in self.observers:
            observer.show_menu_requested(menu_name)

    def notify_show_message_requested(self, message: str) -> None:
        for observer in self.observers:
            observer.show_message_requested(message)

    def notify_change_theme_requested(self, theme_file: str) -> None:
        for observer in self.observers:
            observer.change_theme_requested(theme_file)

    def notify_show_game_requested(self) -> None:
        for observer in self.observers:
            observer.show_game_requested()

    def notify_game_won(self) -> None:
        for observer in self.observers:
            observer.game_won()

    def notify_game_lost(self) -> None:
        for observer in self.observers:
            observer.game_lost()

    def notify_quit_requested(self) -> None:
        for observer in self.observers:
            observer.quit_requested()

    def process_input(self, mouse_x: float, mouse_y: float) -> None:
        raise NotImplementedError()

    def update(self) -> None:
        raise NotImplementedError()

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError()


class MessageGameMode(GameMode):
    def __init__(self, theme: Theme, message: str) -> None:
        super().__init__()
        font_path = theme.locate_resource(theme.message_font)
        self.font = pygame.font.Font(font_path, theme.message_size)

        width, height = 0, 0
        lines = message.split("\n")
        surfaces = []
        for line in lines:
            surface = self.font.render(line, True, pygame.Color(200, 0, 0))
            height += surface.get_height()
            width = max(width, surface.get_width())
            surfaces.append(surface)

        y = 0
        main_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for surface in surfaces:
            x = (main_surface.get_width() - surface.get_width()) // 2
            main_surface.blit(surface, (x, y))
            y += main_surface.get_height()
        self.surface = main_surface

    def process_input(self, mouse_x: float, mouse_y: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.notify_quit_requested()
            elif event.type == pygame.KEYDOWN and event.key in [
                pygame.K_ESCAPE,
                pygame.K_SPACE,
                pygame.K_RETURN,
            ]:
                self.notify_show_menu_requested("main")

    def update(self) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        x = (surface.get_width() - self.surface.get_width()) // 2
        y = (surface.get_height() - self.surface.get_height()) // 2
        surface.blit(self.surface, (x, y))


class MenuGameMode(GameMode):
    def __init__(self, theme: Theme, menu_items: list[dict]) -> None:
        super().__init__()

        title_font_path = theme.locate_resource(theme.title_font)
        menu_font_path = theme.locate_resource(theme.menu_font)
        self.title_font = pygame.font.Font(title_font_path, theme.title_size)
        self.item_font = pygame.font.Font(menu_font_path, theme.menu_size)

        self.menu_width = 0
        self.menu_items = menu_items
        self.text_color = pygame.Color(200, 0, 0)
        for item in self.menu_items:
            surface = self.item_font.render(item["title"], True, self.text_color)
            self.menu_width = max(surface.get_width(), self.menu_width)
            item["surface"] = surface

        self.current_menu_item = 0
        menu_cursor_path = theme.locate_resource(theme.cursor_image)
        self.menu_cursor = pygame.image.load(menu_cursor_path)

    def update(self) -> None:
        pass

    def process_input(self, mouse_x: float, mouse_y: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.notify_quit_requested()
                print("Here")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.notify_show_game_requested()
                elif event.key == pygame.K_DOWN:
                    self.current_menu_item = min(self.current_menu_item + 1, len(self.menu_items) - 1)
                elif event.key == pygame.K_UP:
                    self.current_menu_item = max(self.current_menu_item - 1, 0)
                elif event.key == pygame.K_RETURN:
                    menu_item = self.menu_items[self.current_menu_item]
                    try:
                        action = menu_item["action"]
                        action()
                    except Exception as ex:
                        print(ex)

    def render(self, surface: pygame.Surface) -> None:
        y = 50
        title_surface = self.title_font.render("TANK BATTLEGROUNDS !!!", True, self.text_color)
        x = (surface.get_width() - title_surface.get_width()) // 2
        surface.blit(title_surface, (x, y))
        y += (200 * title_surface.get_height()) // 100

        x = (surface.get_width() - self.menu_width) // 2
        for idx, item in enumerate(self.menu_items):
            item_surface: pygame.Surface = item["surface"]
            surface.blit(item_surface, (x, y))

            if idx == self.current_menu_item:
                cursor_x = x - self.menu_cursor.get_width() - 10
                cursor_y = y + (item_surface.get_height() - self.menu_cursor.get_height()) // 2
                surface.blit(self.menu_cursor, (cursor_x, cursor_y))

            y += (120 * item_surface.get_height()) // 100


class MainMenuGameMode(MenuGameMode):
    def __init__(self, theme: Theme):
        menu_items = [
            {
                "title": "Play",
                "action": lambda: self.notify_show_menu_requested("play"),
            },
            {
                "title": "Select Theme",
                "action": lambda: self.notify_show_menu_requested("theme"),
            },
            {"title": "Quit", "action": lambda: self.notify_quit_requested()},
        ]
        super().__init__(theme, menu_items)


class FindLevelError(ValueError):
    def __init__(self, message: str, *args: Any) -> None:
        self.message = message.format(*args)
        super().__init__(self.message)


class LevelFinder:
    def all(self) -> list[dict[str, Any]]:
        raise NotImplementedError()


class PackagedLevelFinder(LevelFinder):
    def __init__(self, anchor: Package) -> None:
        self.traversable = importlib.resources.files(anchor)

    def all(self) -> list[dict[str, Any]]:
        levels = []
        for item in self.traversable.iterdir():
            if not item.is_file():
                continue
            basename = os.path.basename(str(item))
            name, ext = os.path.splitext(basename)
            if ext != ".tmx":
                continue
            with importlib.resources.as_file(self.traversable.joinpath(basename)) as file:
                levels.append({"name": name, "path": file.resolve()})
        return levels


class DirectoryLevelFinder(LevelFinder):
    def __init__(self, root_dir: Union[str, pathlib.Path]) -> None:
        self.root_dir = pathlib.Path(root_dir)

        if not self.root_dir.is_dir():
            msg = "{} is not a directory"
            raise FindLevelError(msg, self.root_dir)

    def all(self) -> list[dict[str, Any]]:
        levels = []
        for file in self.root_dir.glob("*.tmx"):
            levels.append({"name": file.stem, "path": file.resolve()})
        return levels


class MultiSourceLevelFinder(LevelFinder):
    def __init__(self, *sources: LevelFinder) -> None:
        self.sources = list(sources)

    def all(self) -> list[dict[str, Any]]:
        return [item for source in self.sources for item in source.all()]


class PlayMenuGameMode(MenuGameMode):
    def __init__(self, theme: Theme, level_finder: LevelFinder):
        menu_items = []
        levels = level_finder.all()
        for level in levels:
            menu_items.append({
                "title": level["name"],
                "action": lambda file=str(level["path"]): self.notify_load_level_requested(file),
            })
        menu_items.append(
            {
                "title": "Back",
                "action": lambda: self.notify_show_menu_requested("main"),
            },
        )
        super().__init__(theme, menu_items)


class ThemeMenuGameMode(MenuGameMode):
    def __init__(self, theme: Theme):
        menu_items = []
        for file in os.listdir("."):
            name, ext = os.path.splitext(file)
            if ext != ".json":
                continue
            menu_items.append({
                "title": name,
                "action": lambda file=file: self.notify_change_theme_requested(self.get_theme_path(file)),
            })
        menu_items.append(
            {
                "title": "Back",
                "action": lambda: self.notify_show_menu_requested("main"),
            },
        )
        super().__init__(theme, menu_items)

    def get_theme_path(self, filename: str) -> str:
        level_path = importlib.resources.files("pybattletank.assets").joinpath(filename)
        return str(level_path)


class PlayGameMode(GameMode):
    def load_level(self, theme: Theme, filename: str) -> None:
        self.theme = theme

        loader = LevelLoader(filename)
        loader.run()

        self.game_state = state = loader.state
        self.tile_width = theme.tile_size[0]
        self.tile_height = theme.tile_size[1]

        self.render_width = state.world_size[0] * self.tile_width
        self.render_height = state.world_size[1] * self.tile_height
        self.rescaled_x = 0
        self.rescaled_y = 0
        self.rescaled_scale_x = 1.0
        self.rescaled_scale_y = 1.0

        self.layers = [
            ArrayLayer(theme, theme.ground_tileset, state, state.ground, 0),
            ArrayLayer(theme, theme.walls_tileset, state, state.walls),
            UnitsLayer(theme, theme.units_tileset, state, state.units),
            BulletsLayer(theme, theme.bullets_tileset, state, state.bullets),
            ExplosionsLayer(theme, theme.explosions_tileset),
            SoundLayer(theme),
        ]

        for layer in self.layers:
            self.game_state.add_observer(layer)

        self.player_unit = self.game_state.units[0]
        self.commands: list[Command] = []
        self.game_over = False

    def process_input(self, mouse_x: float, mouse_y: float) -> None:
        dx, dy = 0, 0
        mouse_clicked = False
        movement_keys = {
            pygame.K_d: (1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_s: (0, 1),
            pygame.K_w: (0, -1),
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.notify_quit_requested()
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.notify_show_menu_requested("main")
            elif event.type == pygame.KEYDOWN and event.key in movement_keys:
                dx, dy = movement_keys[event.key]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

        if self.game_over:
            return

        state = self.game_state
        player_unit = self.player_unit
        if dx != 0 or dy != 0:
            self.commands.append(MoveCommand(state, player_unit, (dx, dy)))

        target_cell = (
            mouse_x / self.tile_width - 0.5,
            mouse_y / self.tile_height - 0.5,
        )
        self.commands.append(TargetCommand(state, player_unit, target_cell))

        self.commands.extend([
            TargetCommand(state, unit, player_unit.position) for unit in state.units if unit != player_unit
        ])
        self.commands.extend([
            ShootCommand(state, unit)
            for unit in state.units
            if unit != player_unit and vector_dist(unit.position, player_unit.position) <= state.bullet_range
        ])

        if mouse_clicked:
            self.commands.append(ShootCommand(state, player_unit))

        for bullet in state.bullets:
            self.commands.append(MoveBulletCommand(state, bullet))

        self.commands.append(DeleteDestroyedCommand(state.bullets))

    def update(self) -> None:
        for command in self.commands:
            command.run()
        self.commands.clear()
        self.game_state.epoch += 1

        if not self.player_unit.alive:
            self.game_over = True
            self.notify_game_lost()
        elif not any(unit.alive for unit in self.game_state.units if unit != self.player_unit):
            self.game_over = True
            self.notify_game_won()

    def render(self, surface: pygame.Surface) -> None:
        for layer in self.layers:
            layer.render(surface)


class UserInterface(IGameModeObserver):
    def __init__(self, theme: Theme, locator: AssetLocator, level_finder: LevelFinder) -> None:
        pygame.init()

        self.theme = theme
        self.locator = locator
        self.level_finder = level_finder
        self.render_width = theme.default_window_width
        self.render_height = theme.default_window_height
        self.rescaled_x = 0
        self.rescaled_y = 0
        self.rescaled_scale_x = 1.0
        self.rescaled_scale_y = 1.0

        self.window = pygame.display.set_mode(
            (self.render_width, self.render_height),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE,
        )

        pygame.display.set_caption("pybattletank")
        icon_path = locator.locate("icon.png")
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)

        self.play_game_mode: Optional[PlayGameMode] = None
        self.overlay_game_mode: GameMode = MainMenuGameMode(theme)
        self.overlay_game_mode.add_observer(self)
        self.active_mode = "Overlay"

        if theme.start_music is not None:
            pygame.mixer.music.load(theme.locate_resource(theme.start_music))
            pygame.mixer.music.play(loops=-1)

        self.clock = pygame.time.Clock()
        self.running = True

    def game_won(self) -> None:
        self.show_message("Victory!")
        if self.theme.victory_music is not None:
            pygame.mixer.music.load(self.theme.locate_resource(self.theme.victory_music))
            pygame.mixer.music.play(loops=-1)

    def game_lost(self) -> None:
        self.show_message("GAME OVER")
        if self.theme.fail_music is not None:
            pygame.mixer.music.load(self.theme.locate_resource(self.theme.fail_music))
            pygame.mixer.music.play(loops=-1)

    def load_level_requested(self, filename: str) -> None:
        if self.play_game_mode is None:
            self.play_game_mode = PlayGameMode()
            self.play_game_mode.add_observer(self)

        try:
            self.play_game_mode.load_level(self.theme, filename)
            self.render_width = self.play_game_mode.render_width
            self.render_height = self.play_game_mode.render_height
            self.play_game_mode.update()
            self.active_mode = "Play"
        except Exception as ex:
            print(ex)
            self.play_game_mode = None
            self.show_message("Level loading failed!")

        if self.theme.play_music is not None:
            pygame.mixer.music.load(self.theme.locate_resource(self.theme.play_music))
            pygame.mixer.music.play(loops=-1)

    def get_mouse_pos(self) -> tuple[float, float]:
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = (mouse_pos[0] - self.rescaled_x) / self.rescaled_scale_x
        mouse_y = (mouse_pos[1] - self.rescaled_y) / self.rescaled_scale_y
        return mouse_x, mouse_y

    def show_game_requested(self) -> None:
        if self.play_game_mode is None:
            return
        self.active_mode = "Play"

    def show_menu_requested(self, menu_name: str) -> None:
        if menu_name == "play":
            self.overlay_game_mode = PlayMenuGameMode(self.theme, self.level_finder)
        elif menu_name == "theme":
            self.overlay_game_mode = ThemeMenuGameMode(self.theme)
        else:
            self.overlay_game_mode = MainMenuGameMode(self.theme)

        self.overlay_game_mode.add_observer(self)
        self.active_mode = "Overlay"

    def show_message(self, message: str) -> None:
        self.overlay_game_mode = MessageGameMode(self.theme, message)
        self.overlay_game_mode.add_observer(self)
        self.active_mode = "Overlay"

    def show_message_requested(self, message: str) -> None:
        self.show_message(message)

        if self.theme.start_music is not None:
            pygame.mixer.music.load(self.theme.locate_resource(self.theme.start_music))
            pygame.mixer.music.play(loops=-1)

    def change_theme_requested(self, theme_file: str) -> None:
        try:
            theme = Theme(self.locator, theme_file)
        except Exception as ex:
            print(ex)
            self.show_message(str(ex))
            return

        self.theme = theme
        self.render_width = theme.default_window_width
        self.render_height = theme.default_window_height
        self.play_game_mode = None
        self.show_menu_requested("main")

    def quit_requested(self) -> None:
        self.running = False

    def render(self) -> None:
        render_width = self.render_width
        render_height = self.render_height
        render_surface = pygame.Surface((render_width, render_height))

        if self.play_game_mode is not None:
            self.play_game_mode.render(render_surface)
        else:
            render_surface.fill(pygame.Color(0, 0, 0))

        if self.active_mode == "Overlay":
            dark_surface = pygame.Surface((render_width, render_height), flags=pygame.SRCALPHA)
            dark_surface.fill(pygame.Color(0, 0, 0, 150))
            render_surface.blit(dark_surface, (0, 0))
            self.overlay_game_mode.render(render_surface)

        window_width, window_height = self.window.get_size()
        render_ratio = render_width / render_height
        window_ratio = window_width / window_height
        if window_ratio <= render_ratio:
            rescaled_width = window_width
            rescaled_height = int(window_width / render_ratio)
            self.rescaled_x = 0
            self.rescaled_y = (window_height - rescaled_height) // 2
        else:
            rescaled_width = int(window_height * render_ratio)
            rescaled_height = window_height
            self.rescaled_x = (window_width - rescaled_width) // 2
            self.rescaled_y = 0

        rescaled_surface = pygame.transform.scale(render_surface, (rescaled_width, rescaled_height))
        self.rescaled_scale_x = rescaled_surface.get_width() / render_surface.get_width()
        self.rescaled_scale_y = rescaled_surface.get_height() / render_surface.get_height()
        self.window.blit(rescaled_surface, (self.rescaled_x, self.rescaled_y))

        pygame.display.update()

    async def run(self) -> None:
        while self.running:
            mouse_x, mouse_y = self.get_mouse_pos()
            if self.active_mode == "Overlay":
                self.overlay_game_mode.process_input(mouse_x, mouse_y)
                self.overlay_game_mode.update()
            elif self.play_game_mode is not None:
                self.play_game_mode.process_input(mouse_x, mouse_y)
                try:
                    self.play_game_mode.update()
                except Exception as ex:
                    print(ex)
                    self.play_game_mode = None
                    self.show_message("Error during game update...")
            self.render()
            self.clock.tick(60)
            await asyncio.sleep(0)
