from pygame import sprite
from pygame.sprite import Group

from typing import Tuple

from .functions import load_image


class Stoyka(sprite.Sprite):
    image = load_image("assets/towers/foundations/stoyka.png")

    def __init__(self, coords: Tuple[int, int], *groups: Group) -> None:
        super().__init__(*groups)
        self.image = Stoyka.image
        self.rect = self.image.get_rect()
        self.rect.topleft = coords
