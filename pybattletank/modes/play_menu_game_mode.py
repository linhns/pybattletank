from pybattletank.finders.level_finder import LevelFinder
from pybattletank.layers.theme import Theme

from .menu_game_mode import MenuGameMode


class PlayMenuGameMode(MenuGameMode):
    def __init__(self, theme: Theme, level_finder: LevelFinder):
        menu_items = []
        levels = level_finder.all()
        for level in levels:
            menu_items.append({
                "title": level["name"],
                "action": lambda file=str(level["path"]): self.notify_load_level_requested(file),
            })
        menu_items.append(
            {
                "title": "Back",
                "action": lambda: self.notify_show_menu_requested("main"),
            },
        )
        super().__init__(theme, menu_items)
