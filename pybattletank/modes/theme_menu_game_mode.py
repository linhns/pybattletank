import importlib
import os

from pybattletank.layers.theme import Theme

from .menu_game_mode import MenuGameMode


class ThemeMenuGameMode(MenuGameMode):
    def __init__(self, theme: Theme):
        menu_items = []
        for file in os.listdir("."):
            name, ext = os.path.splitext(file)
            if ext != ".json":
                continue
            menu_items.append({
                "title": name,
                "action": lambda file=file: self.notify_change_theme_requested(self.get_theme_path(file)),
            })
        menu_items.append(
            {
                "title": "Back",
                "action": lambda: self.notify_show_menu_requested("main"),
            },
        )
        super().__init__(theme, menu_items)

    def get_theme_path(self, filename: str) -> str:
        level_path = importlib.resources.files("pybattletank.assets").joinpath(filename)
        return str(level_path)
