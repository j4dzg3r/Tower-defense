import os
import sys
import random
import math

import pygame
from pygame.math import Vector2

pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image



path_w = 45

class Enemy(pygame.sprite.Sprite):
    image = original_image = load_image("towerDefense_tile245.png", colorkey=None)

    def __init__(self, way_points):
        super().__init__(all_sprites)
        self.waypoints = way_points
        self.target_waypoint = 1
        self.pos = Vector2(self.waypoints[0])
        self.speed = 2

        self.angle = self.find_angle(self.target_waypoint)
        self.in_rotation = False
        self.rotation_angle = 0
        self.direction = 0
        self.rotation_values()

        self.original_image = Enemy.original_image
        self.image = pygame.transform.rotate(self.original_image, -self.angle - 90 * self.direction)
        self.rect = self.image.get_rect()
        self.rect.y = self.pos[1]

    def find_angle(self, cur_wp):
        prev, curr, next = self.waypoints[cur_wp - 1], self.waypoints[cur_wp], self.waypoints[cur_wp + 1]
        if next[0] < prev[0] and next[0] < curr[0]:
            return 0
        if next[1] < prev[1] and next[1] < curr[1]:
            return 90
        if next[0] > prev[0] and next[0] > curr[0]:
            return 180
        if next[1] > prev[1] and next[1] > curr[1]:
            return 270

        # fv = Vector2(self.waypoints[cur_wp][0] - self.waypoints[cur_wp - 1][0],
        #              self.waypoints[cur_wp][1] - self.waypoints[cur_wp - 1][1])
        # sv = Vector2(self.waypoints[cur_wp + 1][0] - self.waypoints[cur_wp][0],
        #              self.waypoints[cur_wp + 1][1] - self.waypoints[cur_wp][1])
        # return fv.angle_to(sv)

    def rotate_right(self, rad):
        if self.rotation_angle < 90:
            self.rect.x = rad * math.cos(math.radians(self.angle)) + self.rotation_x
            self.rect.y = rad * math.sin(math.radians(self.angle)) + self.rotation_y
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90 * self.direction)
            self.angle = (self.angle + self.direction) % 360

            self.rotation_angle = (self.rotation_angle + 1) % 360
            all_sprites.draw(screen)
            pygame.display.flip()
        else:
            self.in_rotation = False
            # self.angle -= 1
            # print(-self.angle - 90 * self.direction, self.rotation_angle)
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90 * self.direction)
            self.rotation_angle = 0

            self.pos = (self.rect.x, self.rect.y)

            self.target_waypoint += 1
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos

    def rotation_values(self):
        prev_wp = self.waypoints[self.target_waypoint - 1]
        this_wp = self.waypoints[self.target_waypoint]
        next_wp = self.waypoints[self.target_waypoint + 1]
        signs = ((next_wp[0] - prev_wp[0]) // abs(next_wp[0] - prev_wp[0]),
                 (next_wp[1] - prev_wp[1]) // abs(next_wp[1] - prev_wp[1]))
        clockw_signs = {(1, 1): (-1, 1), (1, -1): (1, 1), (-1, 1): (-1, -1), (-1, -1): (1, -1)}
        anticlockw_signs = {(1, 1): (1, -1), (1, -1): (-1, -1), (-1, 1): (1, 1), (-1, -1): (-1, 1)}
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
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.kill()

        dist = self.movement.length()
        if self.in_rotation:
            self.rotate_right(path_w)
        else:
            if dist >= self.speed:
                if self.target_waypoint < len(self.waypoints) - 1 and dist < path_w:
                    self.in_rotation = True
                    self.rotation_values()
                else:
                    self.pos += self.movement.normalize() * self.speed
            else:
                if dist:
                    self.pos += self.movement.normalize() * dist
                self.target_waypoint += 1

            self.rect.topleft = self.pos

    def update(self):
        self.move()


if __name__ == '__main__':
    # enemy_image = pygame.transform.scale(load_image('enemy_image.png', colorkey='white'), (40, 40))
    enemy_image = load_image('enemy_image.png', colorkey='white')
    f = open("data/levels.txt", encoding="utf8")
    levels_enemies = f.readlines()

    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    running = True

    # waypoints = [(0, 320), (160, 320), (160, 160), (280, 160), (280, 440), (400, 440), (400, 320), (600, 320)]
    waypoints = [(200, 160), (400, 160), (400, 400), (160, 400), (160, 160), (400, 160), (400, 400), (160, 400), (160, 160)]
    enemies_num = 10
    Enemy(waypoints)
    fon = pygame.transform.scale(load_image('circle.png'), (600, 600))

    enemies_counter = 0
    while running:
        screen.fill("white")
        pygame.draw.lines(screen, "grey", False, waypoints)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        pygame.time.wait(15)
