from .game_item import GameItem
from .unit import Unit


class Bullet(GameItem):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit.position, (2, 1))
        self.unit = unit
        self.start_position = unit.position
        self.end_position = unit.weapon_target
