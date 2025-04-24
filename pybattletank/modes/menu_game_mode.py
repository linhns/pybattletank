import pygame

from pybattletank.layers.theme import Theme

from .game_mode import GameMode


class MenuGameMode(GameMode):
    def __init__(self, theme: Theme, menu_items: list[dict]) -> None:
        super().__init__()

        title_font_path = theme.title_font
        menu_font_path = theme.menu_font
        self.title_font = pygame.font.Font(title_font_path, theme.title_size)
        self.item_font = pygame.font.Font(menu_font_path, theme.menu_size)

        self.menu_width = 0
        self.menu_items = menu_items
        self.text_color = pygame.Color(200, 0, 0)
        for item in self.menu_items:
            surface = self.item_font.render(item["title"], True, self.text_color)
            self.menu_width = max(surface.get_width(), self.menu_width)
            item["surface"] = surface

        self.current_menu_item = 0
        menu_cursor_path = theme.cursor_image
        self.menu_cursor = pygame.image.load(menu_cursor_path)

    def update(self) -> None:
        pass

    def process_input(self, mouse_x: float, mouse_y: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.notify_quit_requested()
                print("Here")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.notify_show_game_requested()
                elif event.key == pygame.K_DOWN:
                    self.current_menu_item = min(self.current_menu_item + 1, len(self.menu_items) - 1)
                elif event.key == pygame.K_UP:
                    self.current_menu_item = max(self.current_menu_item - 1, 0)
                elif event.key == pygame.K_RETURN:
                    menu_item = self.menu_items[self.current_menu_item]
                    try:
                        action = menu_item["action"]
                        action()
                    except Exception as ex:
                        print(ex)

    def render(self, surface: pygame.Surface) -> None:
        y = 50
        title_surface = self.title_font.render("TANK BATTLEGROUNDS !!!", True, self.text_color)
        x = (surface.get_width() - title_surface.get_width()) // 2
        surface.blit(title_surface, (x, y))
        y += (200 * title_surface.get_height()) // 100

        x = (surface.get_width() - self.menu_width) // 2
        for idx, item in enumerate(self.menu_items):
            item_surface: pygame.Surface = item["surface"]
            surface.blit(item_surface, (x, y))

            if idx == self.current_menu_item:
                cursor_x = x - self.menu_cursor.get_width() - 10
                cursor_y = y + (item_surface.get_height() - self.menu_cursor.get_height()) // 2
                surface.blit(self.menu_cursor, (cursor_x, cursor_y))

            y += (120 * item_surface.get_height()) // 100
