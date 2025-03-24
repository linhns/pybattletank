import os

import pygame

os.environ["SDL_VIDEO_CENTERED"] = "1"


class GameState:
    def __init__(self) -> None:
        self.x = 120
        self.y = 120

    def update(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Game Loop")
        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.running = True
        self.move_command_x = 0
        self.move_command_y = 0

    def process_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    self.move_command_x = 8
                elif event.key == pygame.K_LEFT:
                    self.move_command_x = -8
                elif event.key == pygame.K_DOWN:
                    self.move_command_y = 8
                elif event.key == pygame.K_UP:
                    self.move_command_y = -8

    def update(self) -> None:
        self.state.update(self.move_command_x, self.move_command_y)

    def render(self) -> None:
        self.window.fill((0, 0, 0))
        pygame.draw.rect(self.window, (0, 0, 255), (self.state.x, self.state.y, 400, 240))
        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)
