class IGameModeObserver:
    def load_level_requested(self, filename: str) -> None:
        pass

    def show_menu_requested(self, menu_name: str) -> None:
        pass

    def show_message_requested(self, message: str) -> None:
        pass

    def change_theme_requested(self, theme_file: str) -> None:
        pass

    def show_game_requested(self) -> None:
        pass

    def game_won(self) -> None:
        pass

    def game_lost(self) -> None:
        pass

    def quit_requested(self) -> None:
        pass
