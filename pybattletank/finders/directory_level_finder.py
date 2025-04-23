import pathlib
from typing import Any, Union

from .level_finder import FindLevelError, LevelFinder


class DirectoryLevelFinder(LevelFinder):
    def __init__(self, root_dir: Union[str, pathlib.Path]) -> None:
        self.root_dir = pathlib.Path(root_dir)

        if not self.root_dir.is_dir():
            msg = "{} is not a directory"
            raise FindLevelError(msg, self.root_dir)

    def all(self) -> list[dict[str, Any]]:
        levels = []
        for file in self.root_dir.glob("*.tmx"):
            levels.append({"name": file.stem, "path": file.resolve()})
        return levels
