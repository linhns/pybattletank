import pygame

from pybattletank.command.command import Command
from pybattletank.command.delete_destroyed_command import DeleteDestroyedCommand
from pybattletank.command.move_bullet_command import MoveBulletCommand
from pybattletank.command.move_command import MoveCommand
from pybattletank.command.shoot_command import ShootCommand
from pybattletank.command.target_command import TargetCommand
from pybattletank.layers.array_layer import ArrayLayer
from pybattletank.layers.bullets_layer import BulletsLayer
from pybattletank.layers.explosions_layer import ExplosionsLayer
from pybattletank.layers.sound_layer import SoundLayer
from pybattletank.layers.theme import Theme
from pybattletank.layers.units_layer import UnitsLayer
from pybattletank.linalg.vector import vector_dist
from pybattletank.state.level_loader import LevelLoader

from .game_mode import GameMode


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
                break
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
