from typing import Optional

from .bullet import Bullet
from .game_state_observer import IGameStateObserver
from .unit import Unit


class GameState:
    def __init__(self) -> None:
        self.world_size = (1, 1)
        self.ground: list[list[Optional[tuple[int, int]]]] = []
        self.walls: list[list[Optional[tuple[int, int]]]] = []
        self.units: list[Unit] = []
        self.bullets: list[Bullet] = []
        self.bullet_speed = 0.1
        self.bullet_range = 4
        self.bullet_delay = 10
        self.epoch = 0
        self.observers: list[IGameStateObserver] = []

    def is_inside(self, position: tuple[float, float]) -> bool:
        return (
            position[0] >= 0
            and position[0] < self.world_size[0]
            and position[1] >= 0
            and position[1] < self.world_size[1]
        )

    def find_unit(self, position: tuple[float, float]) -> Optional[Unit]:
        for unit in self.units:
            if int(unit.position[0]) == int(position[0]) and int(unit.position[1]) == int(position[1]):
                return unit
        return None

    def find_live_unit(self, position: tuple[float, float]) -> Optional[Unit]:
        unit = self.find_unit(position)
        if unit is None or not unit.alive:
            return None
        return unit

    def add_observer(self, observer: IGameStateObserver) -> None:
        self.observers.append(observer)

    def notify_unit_destroyed(self, unit: Unit) -> None:
        for observer in self.observers:
            observer.unit_destroyed(unit)

    def notify_bullet_fired(self, unit: Unit) -> None:
        for observer in self.observers:
            observer.bullet_fired(unit)
