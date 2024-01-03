from math import degrees, atan2
from pygame import sprite
from pygame.sprite import Group
from pygame.draw import circle
from pygame import Surface
from pygame import mask
from pygame import SRCALPHA
from pygame import transform
from pygame import time

from typing import Tuple, Optional

from .enemy import Enemy

from .functions import load_image

from .foundations import Stoyka


# class Missile(sprite.Sprite):
#     image = load_image()
#
#     def __init__(self, *groups: _Group) -> None:
#         super().__init__(*groups)


class DamageRange(sprite.Sprite):
    def __init__(self, coords: Tuple[int, int], d_range: int, *groups: Group) -> None:
        super().__init__(*groups)
        self.range = 64 * d_range
        self.image = Surface((self.range, self.range), SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (coords[0] + 32, coords[1] + 32)
        circle(self.image, "grey100", (32 * d_range, 32 * d_range), 64 * d_range // 2)
        self.image.set_alpha(100)
        self.mask = mask.from_surface(self.image)
        self.detected_enemy: Optional[Enemy] = None
    
    def update(self, screen: Surface, enemy_group: Group) -> None:
        self.detected_enemy = None
        for i in enemy_group:
            if sprite.collide_mask(self, i):
                self.detected_enemy = i
                break
        screen.blit(self.image, self.rect)
    
    def get_detected_enemy(self) -> Optional[Enemy]:
        return self.detected_enemy


class Pukalka(sprite.Sprite):
    image = load_image("weapon_images/turret.png")

    def __init__(self, coords: Tuple[int, int], weapon_group: Group, foundation_group: Group) -> None:
        super().__init__(weapon_group)
        self.image = transform.rotate(Pukalka.image, 0)
        self.rect = self.image.get_rect()
        self.rect.topleft = coords[0], coords[1] - 8
        self.foundation = Stoyka(coords, foundation_group)
        self.damage_range = DamageRange(coords, 4)
        self.damage = 50
        self.delay = 1000
        self.last_shot = time.get_ticks() - self.delay

    def update(self, screen: Surface, enemy_group: Group) -> None:
        self.damage_range.update(screen, enemy_group)
        enemy = self.damage_range.get_detected_enemy()
        if enemy:
            x_my, y_my = self.rect.center
            x_e, y_e = enemy.rect.center
            if x_e - x_my != 0:
                self.image = transform.rotate(Pukalka.image, degrees(atan2(-(y_e - y_my), (x_e - x_my))) - 90)
                self.rect = self.image.get_rect(center=(x_my, y_my))
            if time.get_ticks() - self.last_shot >= self.delay:
                enemy.get_damage(self.damage)
                self.last_shot = time.get_ticks()
