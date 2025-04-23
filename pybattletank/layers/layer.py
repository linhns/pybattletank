import pygame

from pybattletank.state.game_state_observer import IGameStateObserver

from .theme import Theme


class Layer(IGameStateObserver):
    def __init__(self, theme: Theme) -> None:
        self.theme = theme

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError()
