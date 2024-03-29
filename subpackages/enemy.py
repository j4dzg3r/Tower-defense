import math

from pygame.math import Vector2
from pygame import sprite
from pygame import transform
from pygame import Surface
from pygame import SRCALPHA
from pygame import Rect
from pygame.draw import arc
from pygame.time import get_ticks

from itertools import cycle

from typing import List, Tuple, Dict

from .functions import load_image

from .game_menus.shopping_menu import ShoppingMenu

path_w = 60


class Healthbar(sprite.Sprite):
    def __init__(self, x, y, health_bar_group: sprite.Group) -> None:
        super().__init__(health_bar_group)
        self.health = 100
        self.rad = 48
        self.image = Surface((self.rad, self.rad), SRCALPHA)
        arc(self.image, "green", (0, 0, self.rad, self.rad), math.radians(90), math.radians(self.health * 3.6 + 90), 2)

        self.rect = Rect(x, y, self.rad, self.rad)

    def update(self):
        self.image = Surface((self.rad, self.rad), SRCALPHA)
        arc(self.image, "green", (0, 0, self.rad, self.rad), math.radians(90), math.radians(self.health * 3.6 + 90), 2)


class Enemy(sprite.Sprite):
    images = load_image("assets/enemies/demon.png", colorkey=None)

    def __init__(self, way_points: List[Tuple[int, int]], enemy_group: sprite.Group,
                 health_bar_group: sprite.Group) -> None:
        super().__init__(enemy_group)
        self.waypoints = way_points
        self.target_waypoint = 1
        self.pos = Vector2(self.waypoints[0])
        self.speed = 3.5
        
        self.angle = self.find_angle(self.target_waypoint)
        self.in_rotation = False
        self.rotation_angle = 0
        self.direction = 0
        self.rotation_values()

        self.animation_start = get_ticks()
        self.run_animation = iter(cycle([(i, 128) for i in range(0, 512, 64)]))
        self.animation_delay = 40
        self.update_image()

        self.image = Surface((64, 64))
        self.rect = self.image.get_rect()
        self.rect.centery = int(self.pos[1])

        self.healthbar = Healthbar(self.rect.centerx, self.rect.centery, health_bar_group)
        self.HP = 100
        self.cost = 20

    def update_image(self) -> None:
        if get_ticks() - self.animation_start >= self.animation_delay:
            image_rect = next(self.run_animation)
            self.image = Surface((64, 64))
            self.image.blit(Enemy.images, (0, 0), (*image_rect, 64, 64))
            self.image.set_colorkey("black")
            self.image = transform.rotate(self.image.copy(), -self.angle - 90 * self.direction - 90)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.animation_start = get_ticks()

    def find_angle(self, cur_wp: int) -> int:
        prev, curr, next = self.waypoints[cur_wp - 1], self.waypoints[cur_wp], self.waypoints[cur_wp + 1]
        if next[0] < prev[0] and next[0] < curr[0]:
            return 0
        if next[1] < prev[1] and next[1] < curr[1]:
            return 90
        if next[0] > prev[0] and next[0] > curr[0]:
            return 180
        else:
            return 270

    def rotate_right(self, rad):
        if self.rotation_angle < 90 // self.speed:
            self.rect.centerx = rad * math.cos(math.radians(self.angle)) + self.rotation_x
            self.rect.centery = rad * math.sin(math.radians(self.angle)) + self.rotation_y
            self.rect = self.image.get_rect(center=self.rect.center)
            self.angle = (self.angle + self.direction * self.speed) % 360

            self.rotation_angle = (self.rotation_angle + 1) % 360
            self.healthbar.rect.center = self.rect.center
        else:
            self.in_rotation = False
            self.rotation_angle = 0

            self.pos = self.rect.center

            self.target_waypoint += 1
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos

        self.update_image()

    def rotation_values(self):
        prev_wp = self.waypoints[self.target_waypoint - 1]
        this_wp = self.waypoints[self.target_waypoint]
        next_wp = self.waypoints[self.target_waypoint + 1]
        signs = ((next_wp[0] - prev_wp[0]) // abs(next_wp[0] - prev_wp[0]),
                 (next_wp[1] - prev_wp[1]) // abs(next_wp[1] - prev_wp[1]))
        clockw_signs: Dict[Tuple[int, int], Tuple[int, int]] = {(1, 1): (-1, 1), (1, -1): (1, 1), (-1, 1): (-1, -1),
                                                                (-1, -1): (1, -1)}
        anticlockw_signs: Dict[Tuple[int, int], Tuple[int, int]] = {(1, 1): (1, -1), (1, -1): (-1, -1), (-1, 1): (1, 1),
                                                                    (-1, -1): (-1, 1)}
        cross_product = (prev_wp[0] - this_wp[0]) * (next_wp[1] - this_wp[1]) - \
                        (next_wp[0] - this_wp[0]) * (prev_wp[1] - this_wp[1])
        res_signs = anticlockw_signs[signs]

        if cross_product < 0:
            res_signs = clockw_signs[signs]
            if self.direction == -1:
                self.angle += 180
            self.direction = 1


        elif cross_product >= 0:
            res_signs = anticlockw_signs[signs]
            if self.direction == 1:
                self.angle += 180
            self.direction = -1

        self.rotation_x = this_wp[0] + path_w * res_signs[0]
        self.rotation_y = this_wp[1] + path_w * res_signs[1]

    def move(self):
        self.update_image()
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.die("end")

        dist = self.movement.length()
        if self.in_rotation:
            self.rotate_right(path_w)
        else:
            if dist >= self.speed:
                if self.target_waypoint < len(self.waypoints) - 1 and dist < path_w:
                    self.in_rotation = True
                    self.rotation_values()
                    self.rotate_right(path_w)
                else:
                    self.pos += self.movement.normalize() * self.speed
            else:
                if dist:
                    self.pos += self.movement.normalize() * dist
                self.target_waypoint += 1

            self.rect.center = self.pos
            self.healthbar.rect.center = (self.rect.centerx, self.rect.centery)

    def get_damage(self, damage):
        self.HP -= damage
        if self.HP <= 0:
            self.die("tower")
        self.healthbar.health = self.HP
        self.healthbar.update()

    def die(self, cause):
        self.healthbar.kill()
        if cause == 'end':
            pass
        elif cause == 'tower':
            ShoppingMenu.money += self.cost
        elif cause == 'gate':
            pass
        self.kill()

    def update(self):
        self.move()
