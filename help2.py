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
    image = original_image = load_image("enemy_image.png", colorkey="white")

    def __init__(self, way_points):
        super().__init__(all_sprites)
        self.waypoints = way_points
        self.target_waypoint = 1
        self.pos = Vector2(self.waypoints[0])
        self.speed = 2
        self.angle = -90

        self.original_image = Car.original_image
        self.image = pygame.transform.rotate(self.original_image, self.angle + 90)
        self.rect = self.image.get_rect()
        self.rect.y = self.pos[1]

        self.in_rotation = False
        self.rotation_angle = 0


    def rotate_right(self, rad):
        print("pre", self.pos, self.angle, self.rotation_angle, self.rect.x, self.rect.y)
        if self.rotation_angle <= 90:
            pygame.time.wait(5)
            self.rect.x = rad * math.cos(math.radians(self.angle))//1 + self.rotation_x
            self.rect.y = rad * math.sin(math.radians(self.angle))//1 + self.rotation_y + rad
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)
            self.angle += 1
            self.rotation_angle += 1
            # screen.fill('white')
            all_sprites.draw(screen)
            pygame.display.flip()
        else:
            self.angle -= 1

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
                    self.rotation_x = self.rect.x
                    self.rotation_y = self.rect.y
                    print('Rotation BEGINS')
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

waypoints = [(100, RoY), (400, RoY), (400, 400), (200, 400), (200, 200), (300, 200), (300, 300)]
all_sprites = pygame.sprite.Group()
car = Car(waypoints)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # screen.fill("white")
    for point in waypoints:
        screen.fill('red', (point[0], point[1], 4, 4))


    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    pygame.time.wait(5)
