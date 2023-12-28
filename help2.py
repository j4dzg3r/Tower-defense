import os
import sys
import math

import pygame
from pygame.math import Vector2

pygame.init()
size = 600, 600

clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
RoX, RoY, w = 300, 50, 60


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


class Car(pygame.sprite.Sprite):
    image = original_image = load_image("point.png", colorkey="white")

    def __init__(self, way_points):
        super().__init__(all_sprites)
        self.waypoints = way_points
        self.target_waypoint = 1
        self.pos = Vector2(self.waypoints[0])
        self.speed = 2

        self.angle = self.find_angle(self.target_waypoint)

        self.original_image = Car.original_image
        self.image = pygame.transform.rotate(self.original_image, self.angle + 90)
        self.rect = self.image.get_rect()
        self.rect.y = self.pos[1]

        self.in_rotation = False
        self.rotation_angle = 0
        self.direction = 0

    def find_angle(self, cur_wp):
        fv = Vector2(self.waypoints[cur_wp][0] - self.waypoints[cur_wp - 1][0],
                     self.waypoints[cur_wp][1] - self.waypoints[cur_wp - 1][1])
        sv = Vector2(self.waypoints[cur_wp + 1][0] - self.waypoints[cur_wp][0],
                     self.waypoints[cur_wp + 1][1] - self.waypoints[cur_wp][1])
        return sv.angle_to(fv)

    def rotate_right(self, rad):
        # print("pre", self.pos, self.angle, self.rotation_angle, self.rect.x, self.rect.y)
        if self.rotation_angle <= 90:
            self.rect.x = rad * math.cos(math.radians(self.angle)) + self.rotation_x
            self.rect.y = rad * math.sin(math.radians(self.angle)) + self.rotation_y
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)
            # self.angle = (self.angle + self.direction) % 360
            self.angle = (self.angle + self.direction) % 360
            print(self.angle, self.direction)

            # print('angle', self.angle)
            self.rotation_angle = (self.rotation_angle + 1) % 360
            # screen.fill('white')
            all_sprites.draw(screen)
            pygame.display.flip()
        else:
            # self.angle -= 1

            self.in_rotation = False
            self.rotation_angle = 0

            self.pos = (self.rect.x, self.rect.y)
            print("aft", self.pos, self.angle)

            self.target_waypoint += 1
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos

    def move(self):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.kill()

        dist = self.movement.length()
        if self.in_rotation:
            self.rotate_right(60)
        else:
            if dist >= self.speed:
                if self.target_waypoint < len(self.waypoints) - 1 and dist < 60:
                    self.in_rotation = True
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
                            self.angle = 180
                        self.direction = 1


                    elif cross_product >= 0:
                        res_signs = anticlockw_signs[signs]
                        if self.direction == 1:
                            self.angle = 180
                        self.direction = -1

                    print('direction', self.direction)
                    self.rotation_x = this_wp[0] + w * res_signs[0]
                    self.rotation_y = this_wp[1] + w * res_signs[1]
                else:
                    self.pos += self.movement.normalize() * self.speed
            else:
                if dist:
                    self.pos += self.movement.normalize() * dist
                self.target_waypoint += 1

            self.rect.topleft = self.pos
        pygame.time.wait(10)

    def update(self):
        self.move()


waypoints = [(50, 300), (250, 300), (250, 100), (350, 100), (350, 500), (450, 500), (450, 300), (550, 300)]
all_sprites = pygame.sprite.Group()
car = Car(waypoints)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # screen.fill("white")

    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    pygame.time.wait(5)
