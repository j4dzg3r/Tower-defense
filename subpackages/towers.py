from math import degrees, atan2, sqrt, cos, sin, radians
from multiprocessing import set_forkserver_preload
from pygame import sprite
from pygame.sprite import Group
from pygame.draw import circle
from pygame import Surface
from pygame import mask
from pygame import SRCALPHA
from pygame import transform
from pygame import time
from pygame import mouse

from itertools import cycle

from typing import Any, Tuple, Optional

from .enemy import Enemy
from .game_menus.shopping_menu import ShoppingMenu

from .functions import load_image

from .foundations import Stoyka


class Missile(sprite.Sprite):
    image = load_image("assets/towers/missiles/towerDefense_tile272.png")

    def __init__(self, start_coords: Tuple[int, int], enemy: Enemy, *groups: Group) -> None:
        super().__init__(*groups)
        self.damage = 50
        self.speed = 15
        self.target = enemy
        self.image = Missile.image
        self.rect = self.image.get_rect(center=start_coords)
        self.mask = mask.from_surface(self.image)
    
    def update(self, enemy_group: Group) -> None:
        angle = atan2(-(self.target.rect.centery - self.rect.centery), self.target.rect.centerx - self.rect.centerx)
        v_x = cos(angle) * self.speed
        v_y = -sin(angle) * self.speed
        self.rect.center = self.rect.centerx + v_x, self.rect.centery + v_y
        for i in enemy_group:
            if sprite.collide_mask(self, i):
                i.get_damage(self.damage)
                self.kill()
                break
        if self.target.HP <= 0:
            self.kill()


class DamageRange(sprite.Sprite):
    def __init__(self, coords: Tuple[int, int], d_range: int, *groups: Group) -> None:
        super().__init__(*groups)
        self.range = 64 * d_range
        self.image = Surface((self.range, self.range), SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (coords[0] + 32, coords[1] + 32)
        circle(self.image, "grey100", (32 * d_range, 32 * d_range), 64 * d_range // 2)
        self.image.set_alpha(0)
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
    image = load_image("assets/towers/weapons/turret.png")

    def __init__(self, coords: Tuple[int, int], price: float, weapon_group: Group, foundation_group: Group, missile_group: Group) -> None:
        super().__init__(weapon_group)
        self.price = price

        self.image = transform.rotate(Pukalka.image, 0)
        self.rect = self.image.get_rect()
        self.rect.topleft = coords[0], coords[1] - 8
        self.rect_center = self.rect.center
        self.angle = 0

        self.foundation = Stoyka(coords, foundation_group)
        self.damage_range = DamageRange(coords, 4)
        self.delay = 1000
        self.last_shot = time.get_ticks() - self.delay

        self.missile_group = missile_group
        self.sell_button_clicked = False

        self.shift_range = iter(cycle((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)))
        self.shift = next(self.shift_range)

    def show_tower_menu(self, to_show: bool, screen: Surface) -> None:
        if not to_show:
            return
        self.damage_range.image.set_alpha(100)
        sell_image = load_image("assets/shopping_menu_towers/sell_button.png")
        r = sell_image.get_rect(center=(self.rect.centerx + 64, self.rect.centery + 64))
        screen.blit(sell_image, r)
        
        if mouse.get_pressed()[0] == 1 and r.collidepoint(mouse.get_pos()):
            ShoppingMenu.money += 50
            ShoppingMenu.reversed_transaction(ShoppingMenu(), "Pukalka")
            self.destoy_self()

    def update(self, screen: Surface, enemy_group: Group) -> None:
        self.damage_range.image.set_alpha(0)
        self.show_tower_menu(False, screen)
        if self.sell_button_clicked:
            self.damage_range.image.set_alpha(100)
            self.show_tower_menu(True, screen)

        if self.foundation.rect.collidepoint(mouse.get_pos()):
            self.damage_range.image.set_alpha(100)
            if mouse.get_pressed()[0] == 1:
                self.sell_button_clicked = True
        else:
            if mouse.get_pressed()[0] == 1:
                self.sell_button_clicked = False
        self.damage_range.update(screen, enemy_group)

        enemy = self.damage_range.get_detected_enemy()
        x_my, y_my = self.rect_center
        if enemy:
            x_e, y_e = enemy.rect.center
            # It is a default rotation
            if x_e - x_my != 0:
                self.angle = degrees(atan2(-(y_e - y_my), (x_e - x_my)))
                self.image = transform.rotate(Pukalka.image, self.angle - 90)

            if time.get_ticks() - self.last_shot >= self.delay:
                Missile((x_my, y_my), enemy, self.missile_group)
                self.last_shot = time.get_ticks()
                self.shift = next(self.shift_range)
        self.rect = self.image.get_rect(center=(x_my, y_my))
        
        shift_x = cos(radians(self.angle)) * self.shift
        shift_y = -sin(radians(self.angle)) * self.shift

        self.rect.centerx -= shift_x
        self.rect.centery -= shift_y

        if self.shift != 0:
            self.shift = next(self.shift_range)
    
    def destoy_self(self) -> None:
        self.foundation.kill()
        self.damage_range.kill()
        self.kill()
