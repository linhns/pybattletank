from pybattletank.state.bullet import Bullet
from pybattletank.state.game_state import GameState
from pybattletank.state.unit import Unit

from .command import Command


class ShootCommand(Command):
    def __init__(self, state: GameState, unit: Unit) -> None:
        self.state = state
        self.unit = unit

    def run(self) -> None:
        unit = self.unit
        if not unit.alive:
            return

        state = self.state
        if state.epoch - unit.last_bullet_epoch < state.bullet_delay:
            return

        unit.last_bullet_epoch = state.epoch
        state.bullets.append(Bullet(unit))
        state.notify_bullet_fired(unit)
