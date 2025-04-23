from pybattletank.layers.theme import Theme

from .menu_game_mode import MenuGameMode


class MainMenuGameMode(MenuGameMode):
    def __init__(self, theme: Theme):
        menu_items = [
            {
                "title": "Play",
                "action": lambda: self.notify_show_menu_requested("play"),
            },
            {
                "title": "Select Theme",
                "action": lambda: self.notify_show_menu_requested("theme"),
            },
            {"title": "Quit", "action": lambda: self.notify_quit_requested()},
        ]
        super().__init__(theme, menu_items)
