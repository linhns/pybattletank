import importlib
import os
from importlib.resources import Package
from typing import Any

from .level_finder import LevelFinder


class PackagedLevelFinder(LevelFinder):
    def __init__(self, anchor: Package) -> None:
        self.traversable = importlib.resources.files(anchor)

    def all(self) -> list[dict[str, Any]]:
        levels = []
        for item in self.traversable.iterdir():
            if not item.is_file():
                continue
            basename = os.path.basename(str(item))
            name, ext = os.path.splitext(basename)
            if ext != ".tmx":
                continue
            with importlib.resources.as_file(self.traversable.joinpath(basename)) as file:
                levels.append({"name": name, "path": file.resolve()})
        return levels
