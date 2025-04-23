from .game_item import GameItem


class Unit(GameItem):
    def __init__(self, position: tuple[int, int], tile: tuple[int, int]) -> None:
        super().__init__(position, tile)
        self.weapon_target = (0.0, 0.0)
        self.last_bullet_epoch = -100
