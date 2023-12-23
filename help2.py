import os
import sys
import math

import pygame

if __name__ == '__main__':
    pygame.init()
    size = 600, 400

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
        image = original_image =  load_image("enemy_image.png", colorkey="white")

        def __init__(self, *group):
            super().__init__(*group)
            self.image = Car.image
            self.rect = self.image.get_rect()
            self.rect.x = 0
            self.rect.y = RoY
            self.i = 0
            self.direction = 1

        def move(self):
            if self.rect.x < RoX:
                self.rect.x += self.direction
            elif self.i < 90:
                self.i += 1
                pygame.time.wait(1)
                angle = (self.i - 90) * math.pi / 180
                self.rect.x = w * math.cos(angle) + RoX
                self.rect.y = w * math.sin(angle) + RoY + w
                self.image = pygame.transform.rotate(self.original_image, -self.i)

            else:
                self.rect.y += self.direction
            # self.target = (self.waypoints[self.target_waypoint])

        def rotate(self):
            dist = self.target - self.pos
            self.angle = math.degrees(math.atan2(-dist[1], dist[0]))

            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

        def update(self):
            self.move()
            # self.rotate()


    all_sprites = pygame.sprite.Group()
    car = Car(all_sprites)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill("white")
        screen.fill('black', (300, 50, 4, 4))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        pygame.time.wait(5)
