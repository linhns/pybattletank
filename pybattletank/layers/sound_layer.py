from typing import Optional

import pygame

from pybattletank.state.unit import Unit

from .layer import Layer
from .theme import Theme


class SoundLayer(Layer):
    def __init__(self, theme: Theme) -> None:
        super().__init__(theme)
        self.fire_sound: Optional[pygame.mixer.Sound] = None
        self.explosion_sound: Optional[pygame.mixer.Sound] = None

        if theme.fire_sound is not None:
            fire_sound_path = theme.locate_resource(theme.fire_sound)
            self.fire_sound = pygame.mixer.Sound(fire_sound_path)
            self.fire_sound.set_volume(0.2)

        if theme.explosion_sound is not None:
            explosion_sound_path = theme.locate_resource(theme.explosion_sound)
            self.explosion_sound = pygame.mixer.Sound(explosion_sound_path)
            self.explosion_sound.set_volume(0.2)

    def render(self, surface: pygame.Surface) -> None:
        pass

    def unit_destroyed(self, unit: Unit) -> None:
        if self.explosion_sound is not None:
            self.explosion_sound.play()

    def bullets_fired(self, unit: Unit) -> None:
        if self.fire_sound is not None:
            self.fire_sound.play()
