import importlib.resources

import pygame


class GameState:
    def __init__(self) -> None:
        self.world_width = 16
        self.world_height = 10
        self.tank_x = 5
        self.tank_y = 4
        self.tower_xs = [10, 10]
        self.tower_ys = [3, 5]

    def update(self, dx: int, dy: int) -> None:
        self.tank_x += dx
        self.tank_y += dy

        self.tank_x = max(0, min(self.tank_x, self.world_width - 1))
        self.tank_y = max(0, min(self.tank_y, self.world_height - 1))


class UserInterface:
    def __init__(self) -> None:
        pygame.init()
        self.state = GameState()
        self.tile_width = 64
        self.tile_height = 64

        path = importlib.resources.files("pybattletank.assets").joinpath("units.png")
        self.units_tileset = pygame.image.load(path)

        window_width = self.state.world_width * self.tile_width
        window_height = self.state.world_height * self.tile_height
        self.window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Game Loop")

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
        self.state.update(self.tank_dx, self.tank_dy)

    def draw_unit(self, cell_x: int, cell_y: int, base_tile_x: int, base_tile_y: int) -> None:
        sprite_x = cell_x * self.tile_width
        sprite_y = cell_y * self.tile_height
        tile_x = base_tile_x * self.tile_width
        tile_y = base_tile_y * self.tile_height
        tile_rect = pygame.Rect(tile_x, tile_y, self.tile_width, self.tile_height)
        self.window.blit(self.units_tileset, (sprite_x, sprite_y), tile_rect)

        # Gun
        tile_x = 4 * self.tile_width
        tile_y = 1 * self.tile_height
        tile_rect = pygame.Rect(tile_x, tile_y, self.tile_width, self.tile_height)
        self.window.blit(self.units_tileset, (sprite_x, sprite_y), tile_rect)

    def render(self) -> None:
        self.window.fill((0, 0, 0))
        state = self.state
        for x, y in zip(state.tower_xs, state.tower_ys):
            self.draw_unit(x, y, 0, 1)
        self.draw_unit(state.tank_x, state.tank_y, 1, 0)

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)
