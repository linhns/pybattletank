import importlib.resources
import math
from collections.abc import Sequence
from typing import Any, Optional

import pygame


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


class GameState:
    def __init__(self) -> None:
        self.world_size = (16, 10)
        self.ground: list[list[Optional[tuple[int, int]]]] = [
            [
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
            ],
            [
                (5, 1),
                (5, 1),
                (7, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (7, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 1),
                (5, 1),
                (5, 1),
                (6, 4),
                (7, 2),
                (7, 2),
            ],
            [
                (5, 1),
                (6, 1),
                (5, 1),
                (5, 1),
                (6, 1),
                (6, 2),
                (5, 1),
                (6, 1),
                (6, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (6, 1),
                (5, 1),
            ],
            [
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 1),
                (6, 2),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (5, 1),
                (7, 1),
            ],
            [
                (5, 1),
                (7, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 5),
                (7, 2),
                (7, 2),
                (7, 2),
                (7, 2),
                (7, 2),
                (7, 2),
                (7, 2),
                (8, 5),
                (5, 1),
                (5, 1),
            ],
            [
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 1),
                (6, 2),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (5, 1),
                (7, 1),
            ],
            [
                (6, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (5, 1),
                (5, 1),
                (7, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (7, 1),
                (5, 1),
            ],
            [
                (5, 1),
                (5, 1),
                (6, 4),
                (7, 2),
                (7, 2),
                (8, 4),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (6, 2),
                (5, 1),
                (5, 1),
            ],
            [
                (5, 1),
                (5, 1),
                (6, 2),
                (5, 1),
                (5, 1),
                (7, 1),
                (5, 1),
                (5, 1),
                (6, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (7, 4),
                (7, 2),
                (7, 2),
            ],
            [
                (5, 1),
                (5, 1),
                (6, 2),
                (6, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
                (5, 1),
            ],
        ]
        self.walls = [
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (1, 3),
                (1, 1),
                (1, 1),
                (1, 1),
                (1, 1),
                (1, 1),
                (1, 1),
            ],
            [None, None, None, None, None, None, None, None, None, (2, 1), None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None, (2, 1), None, None, (1, 3), (1, 1), (0, 3), None],
            [None, None, None, None, None, None, None, (1, 1), (1, 1), (3, 3), None, None, (2, 1), None, (2, 1), None],
            [None, None, None, None, None, None, None, None, None, None, None, None, (2, 1), None, (2, 1), None],
            [None, None, None, None, None, None, None, (1, 1), (1, 1), (0, 3), None, None, (2, 1), None, (2, 1), None],
            [None, None, None, None, None, None, None, None, None, (2, 1), None, None, (2, 1), None, (2, 1), None],
            [None, None, None, None, None, None, None, None, None, (2, 1), None, None, (2, 3), (1, 1), (3, 3), None],
            [None, None, None, None, None, None, None, None, None, (2, 1), None, None, None, None, None, None],
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (2, 3),
                (1, 1),
                (1, 1),
                (1, 1),
                (1, 1),
                (1, 1),
                (1, 1),
            ],
        ]
        self.units = [
            Unit(self, (1, 9), (1, 0)),
            Unit(self, (6, 3), (0, 2)),
            Unit(self, (6, 5), (0, 2)),
            Unit(self, (13, 3), (0, 1)),
            Unit(self, (13, 6), (0, 1)),
        ]
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


class Layer(IGameStateObserver):
    def __init__(self, ui: "UserInterface", image_filename: str) -> None:
        self.ui = ui
        self.tileset = pygame.image.load(image_filename)

    def draw_tile(
        self,
        surface: pygame.Surface,
        position: tuple[int, int],
        tile_coords: tuple[int, int],
        angle: Optional[float] = None,
    ) -> None:
        tile_width = self.ui.tile_width
        tile_height = self.ui.tile_height
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

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError()


class ArrayLayer(Layer):
    def __init__(
        self,
        ui: "UserInterface",
        image_filename: str,
        state: GameState,
        array: list[list[Optional[tuple[int, int]]]],
        surface_flags: int = pygame.SRCALPHA,
    ) -> None:
        super().__init__(ui, image_filename)
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


class UnitsLayer(Layer):
    def __init__(self, ui: "UserInterface", image_filename: str, state: GameState, units: list[Unit]) -> None:
        super().__init__(ui, image_filename)
        self.state = state
        self.units = units

    def render(self, surface: pygame.Surface) -> None:
        for unit in self.units:
            self.draw_tile(surface, unit.position, unit.tile, unit.orientation)

            dir_x = unit.weapon_target[0] - unit.position[0]
            dir_y = unit.weapon_target[1] - unit.position[1]
            angle = math.atan2(-dir_x, -dir_y) * 180 / math.pi

            self.draw_tile(surface, unit.position, (4, 1), angle)


class BulletsLayer(Layer):
    def __init__(self, ui: "UserInterface", image_filename: str, state: GameState, bullets: list[Bullet]) -> None:
        super().__init__(ui, image_filename)
        self.state = state
        self.bullets = bullets

    def render(self, surface: pygame.Surface) -> None:
        for bullet in self.bullets:
            if bullet.alive:
                self.draw_tile(surface, bullet.position, bullet.tile, bullet.orientation)


class ExplosionsLayer(Layer):
    def __init__(self, ui: "UserInterface", image_filename: str) -> None:
        super().__init__(ui, image_filename)
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


class UserInterface:
    def __init__(self) -> None:
        pygame.init()
        self.state = GameState()
        self.tile_width = 64
        self.tile_height = 64

        self.render_width = self.state.world_size[0] * self.tile_width
        self.render_height = self.state.world_size[1] * self.tile_height
        self.rescaled_x = 0
        self.rescaled_y = 0
        self.rescaled_scale_x = 1.0
        self.rescaled_scale_y = 1.0

        state = self.state
        background_path = importlib.resources.files("pybattletank.assets").joinpath("ground.png")
        walls_path = importlib.resources.files("pybattletank.assets").joinpath("walls.png")
        units_path = importlib.resources.files("pybattletank.assets").joinpath("units.png")
        bullets_path = importlib.resources.files("pybattletank.assets").joinpath("explosions.png")
        explosions_path = bullets_path
        self.layers = [
            ArrayLayer(self, str(background_path), state, state.ground),
            ArrayLayer(self, str(walls_path), state, state.walls),
            UnitsLayer(self, str(units_path), state, state.units),
            BulletsLayer(self, str(bullets_path), state, state.bullets),
            ExplosionsLayer(self, str(explosions_path)),
        ]

        for layer in self.layers:
            state.add_observer(layer)

        window_width = 800
        window_height = (window_width * self.render_height) // self.render_width
        self.window = pygame.display.set_mode(
            (window_width, window_height),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE,
        )
        pygame.display.set_caption("pybattletank")

        icon_path = importlib.resources.files("pybattletank.assets").joinpath("icon.png")
        icon = pygame.image.load(str(icon_path))
        pygame.display.set_icon(icon)

        self.player_unit = self.state.units[0]
        self.commands: list[Command] = []

        self.clock = pygame.time.Clock()
        self.running = True

    def process_input(self) -> None:
        dx, dy = 0, 0
        mouse_clicked = False
        movement_keys = {pygame.K_RIGHT: (1, 0), pygame.K_LEFT: (-1, 0), pygame.K_DOWN: (0, 1), pygame.K_UP: (0, -1)}
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                break
            elif event.type == pygame.KEYDOWN and event.key in movement_keys:
                dx, dy = movement_keys[event.key]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

        state = self.state
        player_unit = self.player_unit
        if dx != 0 or dy != 0:
            self.commands.append(MoveCommand(state, player_unit, (dx, dy)))

        mouse_pos = pygame.mouse.get_pos()
        mouse_x = (mouse_pos[0] - self.rescaled_x) / self.rescaled_scale_x
        mouse_y = (mouse_pos[1] - self.rescaled_y) / self.rescaled_scale_y
        target_cell = (mouse_x / self.tile_width - 0.5, mouse_y / self.tile_height - 0.5)
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
        self.state.epoch += 1

    def render_world(self, surface: pygame.Surface) -> None:
        surface.fill((0, 64, 0))
        for layer in self.layers:
            layer.render(surface)

    def render(self) -> None:
        render_width = self.render_width
        render_height = self.render_height
        render_surface = pygame.Surface((render_width, render_height))
        self.render_world(render_surface)

        window_width, window_height = self.window.get_size()
        render_ratio = render_width / render_height
        window_ratio = window_width / window_height
        if window_ratio <= render_ratio:
            rescaled_width = window_width
            rescaled_height = int(window_width / render_ratio)
            rescaled_x = 0
            rescaled_y = (window_height - rescaled_height) // 2
        else:
            rescaled_width = int(window_height * render_ratio)
            rescaled_height = window_height
            rescaled_x = (window_width - rescaled_width) // 2
            rescaled_y = 0

        rescaled_surface = pygame.transform.scale(render_surface, (rescaled_width, rescaled_height))
        self.rescaled_scale_x = rescaled_surface.get_width() / render_surface.get_width()
        self.rescaled_scale_y = rescaled_surface.get_height() / render_surface.get_height()
        self.window.blit(rescaled_surface, (rescaled_x, rescaled_y))

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)
