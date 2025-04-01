import importlib.resources
import math

import pygame


class Unit:
    def __init__(self, state: "GameState", position: tuple[int, int], tile: tuple[int, int]) -> None:
        self.state = state
        self.position = position
        self.tile = tile
        self.orientation = 0
        self.weapon_target = (0.0, 0.0)


class GameState:
    def __init__(self) -> None:
        self.world_size = (16, 10)
        self.ground: list[list[tuple[int, int] | None]] = [
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


class Layer:
    def __init__(self, ui: "UserInterface", image_filename: str) -> None:
        self.ui = ui
        self.tileset = pygame.image.load(image_filename)

    def draw_tile(
        self,
        surface: pygame.Surface,
        position: tuple[int, int],
        tile_coords: tuple[int, int],
        angle: float | None = None,
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
        self, ui: "UserInterface", image_filename: str, state: GameState, array: list[list[tuple[int, int] | None]]
    ) -> None:
        super().__init__(ui, image_filename)
        self.state = state
        self.array = array

    def render(self, surface: pygame.Surface) -> None:
        for y in range(self.state.world_size[1]):
            for x in range(self.state.world_size[0]):
                tile = self.array[y][x]
                if tile is not None:
                    self.draw_tile(surface, (x, y), tile)


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
        self.layers = [
            ArrayLayer(self, str(background_path), state, state.ground),
            ArrayLayer(self, str(walls_path), state, state.walls),
            UnitsLayer(self, str(units_path), state, state.units),
        ]

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

    def process_keypresses(self) -> None:
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_UP:
                    dy = -1
        if dx != 0 or dy != 0:
            command = MoveCommand(self.state, self.player_unit, (dx, dy))
            self.commands.append(command)

    def process_mouseclicks(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = (mouse_pos[0] - self.rescaled_x) / self.rescaled_scale_x
        mouse_y = (mouse_pos[1] - self.rescaled_y) / self.rescaled_scale_y
        target_cell = (mouse_x / self.tile_width - 0.5, mouse_y / self.tile_height - 0.5)
        command = TargetCommand(self.state, self.player_unit, target_cell)
        self.commands.append(command)

        for unit in self.state.units:
            if unit != self.player_unit:
                command = TargetCommand(self.state, unit, self.player_unit.position)
                self.commands.append(command)

    def process_input(self) -> None:
        self.process_keypresses()
        self.process_mouseclicks()

    def update(self) -> None:
        for command in self.commands:
            command.run()
        self.commands.clear()

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
        self.window.blit(rescaled_surface, (rescaled_x, rescaled_y))

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)
