class GameItem:
    def __init__(self, position: tuple[int, int], tile: tuple[int, int]) -> None:
        self.alive = True
        self.position = position
        self.tile = tile
        self.orientation = 0.0
