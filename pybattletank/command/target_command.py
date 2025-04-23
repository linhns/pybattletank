from pybattletank.state.game_state import GameState
from pybattletank.state.unit import Unit

from .command import Command


class TargetCommand(Command):
    def __init__(self, state: GameState, unit: Unit, target: tuple[float, float]) -> None:
        self.state = state
        self.unit = unit
        self.target = target

    def run(self) -> None:
        self.unit.weapon_target = self.target
