from pybattletank.linalg.vector import vector_add, vector_dist, vector_normalize, vector_sub
from pybattletank.state.bullet import Bullet
from pybattletank.state.game_state import GameState

from .command import Command


class MoveBulletCommand(Command):
    def __init__(self, state: GameState, bullet: Bullet) -> None:
        self.state = state
        self.bullet = bullet

    def run(self) -> None:
        bullet = self.bullet
        state = self.state
        direction = vector_sub(bullet.end_position, bullet.start_position)
        direction = vector_normalize(direction)
        new_pos = vector_add(bullet.position, direction, state.bullet_speed)

        if not state.is_inside(new_pos):
            bullet.alive = False
            return

        dir_x, dir_y = direction
        if (
            (dir_x >= 0 and new_pos[0] >= bullet.end_position[0])
            or (dir_x < 0 and new_pos[0] <= bullet.end_position[0])
        ) and (
            (dir_y >= 0 and new_pos[1] >= bullet.end_position[1])
            or (dir_y < 0 and new_pos[1] <= bullet.end_position[1])
        ):
            bullet.alive = False
            return

        if vector_dist(new_pos, bullet.start_position) > state.bullet_range:
            bullet.alive = False
            return

        new_center_pos = vector_add(new_pos, (0.5, 0.5))
        unit = state.find_live_unit(new_center_pos)
        if unit is not None and unit != bullet.unit:
            bullet.alive = False
            unit.alive = False
            state.notify_unit_destroyed(unit)
            return

        bullet.position = new_pos  # type: ignore[assignment]
