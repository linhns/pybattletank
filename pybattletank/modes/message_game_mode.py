import pygame

from pybattletank.layers.theme import Theme

from .game_mode import GameMode


class MessageGameMode(GameMode):
    def __init__(self, theme: Theme, message: str) -> None:
        super().__init__()
        font_path = theme.message_font
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
