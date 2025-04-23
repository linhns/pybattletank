import asyncio
from typing import Optional

import pygame

from pybattletank.finders.level_finder import LevelFinder
from pybattletank.layers.theme import Theme
from pybattletank.locators.asset_locator import AssetLocator
from pybattletank.modes.game_mode import GameMode
from pybattletank.modes.game_mode_observer import IGameModeObserver
from pybattletank.modes.main_menu_game_mode import MainMenuGameMode
from pybattletank.modes.message_game_mode import MessageGameMode
from pybattletank.modes.play_game_mode import PlayGameMode
from pybattletank.modes.play_menu_game_mode import PlayMenuGameMode
from pybattletank.modes.theme_menu_game_mode import ThemeMenuGameMode


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
