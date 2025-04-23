from typing import Any


class FindLevelError(ValueError):
    def __init__(self, message: str, *args: Any) -> None:
        self.message = message.format(*args)
        super().__init__(self.message)


class LevelFinder:
    def all(self) -> list[dict[str, Any]]:
        raise NotImplementedError()
