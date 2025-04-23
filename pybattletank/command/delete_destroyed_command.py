from collections.abc import Sequence

from pybattletank.state.game_item import GameItem

from .command import Command


class DeleteDestroyedCommand(Command):
    def __init__(self, items: Sequence[GameItem]) -> None:
        self.items = items

    def run(self) -> None:
        self.items = [item for item in self.items if item.alive]
