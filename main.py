import os
import sys
import random
import math

import pygame
from pygame.math import Vector2

if __name__ == '__main__':
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


    enemy_image = pygame.transform.scale(load_image('enemy_image.png', colorkey='white'), (40, 40))
    f = open("data/levels.txt", encoding="utf8")
    levels_enemies = f.readlines()


    class Enemy(pygame.sprite.Sprite):
        def __init__(self, way_points):
            super().__init__(all_sprites, enemy_group)
            self.waypoints = way_points
            self.target_waypoint = 1
            self.pos = Vector2(self.waypoints[0])
            self.speed = 2
            self.angle = 0

            self.original_image = enemy_image
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

        def update(self):
            self.move()
            self.rotate()

        def move(self):
            if self.target_waypoint < len(self.waypoints):
                self.target = Vector2(self.waypoints[self.target_waypoint])
                self.movement = self.target - self.pos
            else:
                self.kill()
            dist = self.movement.length()
            if dist >= self.speed:
                self.pos += self.movement.normalize() * self.speed
            else:
                if dist:
                    self.pos += self.movement.normalize() * dist
                self.target_waypoint += 1

        def rotate(self):
            dist = self.target - self.pos
            self.angle = math.degrees(math.atan2(-dist[1], dist[0]))

            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos


    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    running = True

    waypoints = [(0, 320), (160, 320), (160, 160), (280, 160), (280, 440), (400, 440), (400, 320), (600, 320)]
    enemies_num = 10
    Enemy(waypoints)
    fon = pygame.transform.scale(load_image('map1.png'), (600, 600))

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
