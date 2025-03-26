import importlib.resources

import pygame


class GameState:
    def __init__(self) -> None:
        self.world_size = (16, 10)
        self.units = [Tank(self, (5, 4), (1, 0)), Tower(self, (10, 3), (0, 1)), Tower(self, (10, 5), (0, 1))]

    def update(self, move_tank_command: tuple[int, int]) -> None:
        for unit in self.units:
            unit.move(move_tank_command)


class Unit:
    def __init__(self, state: GameState, position: tuple[int, int], tile: tuple[int, int]) -> None:
        self.state = state
        self.position = position
        self.tile = tile

    def move(self, move_vector: tuple[int, int]) -> None:
        raise NotImplementedError()


class Tank(Unit):
    def move(self, move_vector: tuple[int, int]) -> None:
        x, y = self.position
        dx, dy = move_vector
        nx, ny = (x + dx, y + dy)

        world_width, world_height = self.state.world_size
        if nx < 0 or nx >= world_width or ny < 0 or ny >= world_height:
            return
        for unit in self.state.units:
            if (nx, ny) == unit.position:
                return
        self.position = (nx, ny)


class Tower(Unit):
    def move(self, move_vector: tuple[int, int]) -> None:
        pass


class UserInterface:
    def __init__(self) -> None:
        pygame.init()
        self.state = GameState()
        self.tile_width = 64
        self.tile_height = 64

        self.render_width = self.state.world_size[0] * self.tile_width
        self.render_height = self.state.world_size[1] * self.tile_height

        path = importlib.resources.files("pybattletank.assets").joinpath("units.png")
        self.units_tileset = pygame.image.load(str(path))

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

        self.tank_dx = 0
        self.tank_dy = 0

        self.clock = pygame.time.Clock()
        self.running = True

    def process_input(self) -> None:
        self.tank_dx = 0
        self.tank_dy = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    self.tank_dx = 1
                elif event.key == pygame.K_LEFT:
                    self.tank_dx = -1
                elif event.key == pygame.K_DOWN:
                    self.tank_dy = 1
                elif event.key == pygame.K_UP:
                    self.tank_dy = -1

    def update(self) -> None:
        self.state.update((self.tank_dx, self.tank_dy))

    def draw_unit(self, surface: pygame.Surface, unit: Unit) -> None:
        sprite_x = unit.position[0] * self.tile_width
        sprite_y = unit.position[1] * self.tile_height

        tile_x = unit.tile[0] * self.tile_width
        tile_y = unit.tile[1] * self.tile_height
        tile_rect = pygame.Rect(tile_x, tile_y, self.tile_width, self.tile_height)
        surface.blit(self.units_tileset, (sprite_x, sprite_y), tile_rect)

        # Gun
        tile_x = 4 * self.tile_width
        tile_y = 1 * self.tile_height
        tile_rect = pygame.Rect(tile_x, tile_y, self.tile_width, self.tile_height)
        surface.blit(self.units_tileset, (sprite_x, sprite_y), tile_rect)

    def render_world(self, surface: pygame.Surface) -> None:
        surface.fill((0, 64, 0))
        state = self.state
        for unit in state.units:
            self.draw_unit(surface, unit)

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
