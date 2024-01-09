import pygame
from pygame import sprite
from pygame.sprite import Group
from pygame import Surface
from pygame import SRCALPHA
from pygame import Rect

from pygame import mouse
from pygame.font import Font
from pygame.transform import grayscale

from typing import List, Dict

from ..functions import load_image


class GameEndMenu(sprite.Sprite):
    star_images = [load_image(F"assets/star_animation/star_{i}.png") for i in range(1, 9)]

    def __init__(self) -> None:
        super().__init__()
        self.rect = pygame.Rect(0, 0, 600, 500)
        self.image = pygame.Surface((600, 500), SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color("#dbb20b"), self.rect)
        self.original_image = pygame.Surface((600, 500), SRCALPHA)
        self.original_image.blit(self.image, (0, 0))

        self.name_font = Font(None, 50)
        self.font = Font(None, 30)
        self.image_num = 0
        self.last_animation = pygame.time.get_ticks()
        self.image.set_alpha(230)

    def update(self, screen: Surface, result: int):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_animation >= 30:
            self.image.blit(self.original_image, (0, 0))
            if self.image_num < 8:
                now_im = GameEndMenu.star_images[self.image_num]
                if result < 0:
                    self.image.blit(grayscale(now_im), (150 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                else:
                    self.image.blit(now_im, (150 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                self.image_num += 1
                self.last_animation = pygame.time.get_ticks()
            elif self.image_num < 17:
                now_im = GameEndMenu.star_images[self.image_num - 9]
                if result < 1:
                    self.image.blit(grayscale(now_im), (450 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                else:
                    self.image.blit(now_im, (450 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                self.image_num += 1
                self.last_animation = pygame.time.get_ticks()
            elif self.image_num < 26:
                now_im = GameEndMenu.star_images[self.image_num - 18]
                if result < 2:
                    self.image.blit(grayscale(now_im), (300 - now_im.get_width() // 2, 90 - now_im.get_height() // 2))
                else:
                    self.image.blit(now_im, (300 - now_im.get_width() // 2, 90 - now_im.get_height() // 2))
                self.image_num += 1
                self.last_animation = pygame.time.get_ticks()
            if self.image_num == 8 or self.image_num == 17 or self.image_num == 26:
                self.original_image.blit(self.image, (0, 0))
                self.image_num += 1
            if result == 3:
                print('Molodets!')
