import pygame

from .game_mode_observer import IGameModeObserver


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
