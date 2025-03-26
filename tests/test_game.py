from pybattletank.game import GameState


def test_non_move() -> None:
    state = GameState()
    old_positions = [unit.position for unit in state.units]
    state.update((0, 0))
    new_positions = [unit.position for unit in state.units]
    assert old_positions == new_positions
