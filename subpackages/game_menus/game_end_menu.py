import pygame
from pygame import sprite
from pygame.sprite import Group
from pygame import Surface
from pygame import SRCALPHA
from pygame import Rect

from pygame import mouse
from pygame.font import Font

from typing import List, Dict

from ..functions import load_image


class GameEndMenu(sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.rect = pygame.Rect(0,0, 600, 500)
        self.image = pygame.Surface((600, 500), SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color("#facf23"), self.rect, 4)

        self.name_font = Font(None, 50)
        self.font = Font(None, 30)

    def update(self, screen: Surface):
        pass

