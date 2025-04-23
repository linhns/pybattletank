from pybattletank.state.game_state import GameState
from pybattletank.state.unit import Unit

from .command import Command


class MoveCommand(Command):
    def __init__(self, state: GameState, unit: Unit, move_vector: tuple[int, int]) -> None:
        self.state = state
        self.unit = unit
        self.move_vector = move_vector

    def run(self) -> None:
        if not self.unit.alive:
            return

        dx, dy = self.move_vector
        if dx < 0:
            self.unit.orientation = 90
        if dx > 0:
            self.unit.orientation = -90
        if dy < 0:
            self.unit.orientation = 0
        if dy < 0:
            self.unit.orientation = 180

        x, y = self.unit.position
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= self.state.world_size[0] or ny < 0 or ny >= self.state.world_size[1]:
            return
        if self.state.walls[ny][nx] is not None:
            return
        for unit in self.state.units:
            if (nx, ny) == unit.position:
                return
        self.unit.position = (nx, ny)
