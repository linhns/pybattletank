from .unit import Unit


class IGameStateObserver:
    def unit_destroyed(self, unit: Unit) -> None:
        pass

    def bullet_fired(self, unit: Unit) -> None:
        pass
