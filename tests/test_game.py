from pybattletank.game import GameState


def test_is_inside() -> None:
    state = GameState()
    assert state.is_inside((0, 0))
    assert state.is_inside((15, 9))
    assert not state.is_inside((16, 10))
