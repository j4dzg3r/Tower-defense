from pygame import sprite
from pygame.sprite import Group
from pygame.draw import circle
from pygame import Surface
from pygame import mask
from pygame import SRCALPHA
from pygame import mouse

from typing import Any, Tuple

from .functions import load_image

from .foundations import Stoyka


class DamageRange(sprite.Sprite):
    def __init__(self, coords: Tuple[int, int], d_range: int, *groups: Group) -> None:
        super().__init__(*groups)
        self.range = 64 * d_range
        self.image = Surface((self.range, self.range), SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (coords[0] + 32, coords[1] + 32)
        circle(self.image, "grey100", (32 * 4, 32 * 4), 64 * 2)
        self.image.set_alpha(100)
        self.mask = mask.from_surface(self.image)
    
    def update(self, screen: Surface, enemy_group: Group) -> None:
        self.image.set_alpha(100)
        for i in enemy_group:
            if sprite.collide_mask(self, i):
                self.image.set_alpha(255)
        screen.blit(self.image, self.rect)


class Pukalka(sprite.Sprite):
    image = load_image("weapon_images/turret.png")

    def __init__(self, coords: Tuple[int, int], weapon_group: Group, foundation_group: Group) -> None:
        super().__init__(weapon_group)
        self.image = Pukalka.image
        self.rect = self.image.get_rect()
        self.rect.topleft = coords
        self.rect.y -= 8
        self.foundation = Stoyka(coords, foundation_group)
        self.damage_range = DamageRange(coords, 4)

    def update(self, screen: Surface, enemy_group: Group) -> None:
        self.damage_range.update(screen, enemy_group)
