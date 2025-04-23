from typing import Any

from .level_finder import LevelFinder


class MultiSourceLevelFinder(LevelFinder):
    def __init__(self, *sources: LevelFinder) -> None:
        self.sources = list(sources)

    def all(self) -> list[dict[str, Any]]:
        return [item for source in self.sources for item in source.all()]
