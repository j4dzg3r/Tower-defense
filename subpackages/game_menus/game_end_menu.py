from pygame import sprite, Surface, Rect, SRCALPHA
from pygame import event as pgevent
from pygame import mouse

from pygame.sprite import Group
from pygame.transform import scale

from pygame import mouse
from pygame.font import Font
from pygame.transform import grayscale
from pygame.time import get_ticks
from pygame import MOUSEMOTION, MOUSEBUTTONUP
from pygame.mouse import get_pressed
from typing import List, Dict

from ..functions import load_image
from ..errors import QuitError


class MenuButton(sprite.Sprite):
    images = load_image("assets/game_end_menu/buttons.png", colorkey=None)

    def __init__(self, but_type: str, game_end_menu_button_group):
        super().__init__(game_end_menu_button_group)
        y_from_type = {'next': 0, 'pause': 1, 'menu': 2, 'info': 3, 'restart': 4, 'music': 5, 'sound': 6}
        self.type = but_type
        self.unselect_image = Surface((75, 80), SRCALPHA)
        self.select_image = Surface((75, 80), SRCALPHA)
        self.image = Surface((75, 80), SRCALPHA)
        self.unselect_image.blit(MenuButton.images, (0, 0), (0, y_from_type[self.type] * 80, 75, 80))
        self.select_image.blit(MenuButton.images, (0, 0), (75, y_from_type[self.type] * 80, 75, 80))

        self.image.blit(self.unselect_image, (0, 0))
        self.rect = self.image.get_rect()


class GameEndMenu(sprite.Sprite):
    frame_image = load_image("assets/game_end_menu/frame_shadow.png")
    star_images = [load_image(f"assets/game_end_menu/star_{i}.png") for i in range(1, 9)]
    perf_image = load_image("assets/game_end_menu/perfect.png")

    def __init__(self) -> None:
        super().__init__()
        self.rect = Rect(0, 0, 600, 500)
        self.image = GameEndMenu.frame_image
        self.image.blit(GameEndMenu.frame_image, (0, 0))
        self.original_image = Surface((600, 500), SRCALPHA)
        self.original_image.blit(GameEndMenu.frame_image, (0, 0))
        self.name_font = Font(None, 50)
        self.font = Font(None, 30)
        self.image_num = 0
        self.last_animation = get_ticks()
        # self.image.set_alpha(230)
        self.alpha_now = 5
        print('New game ned menu')

    def update(self, screen: Surface, result: int, game_end_menu_button_group: Group) -> None:
        if len(game_end_menu_button_group) == 0:
            if result >= 0:
                self.next_button = MenuButton('next', game_end_menu_button_group)
                self.next_button.rect.topleft = (660, 580)
            # else:
            # self.tip_button = MenuButton('info', self.game_end_menu_group)
            # self.tip_button.rect.pos = (130, 300)
            self.restart_button = MenuButton('restart', game_end_menu_button_group)
            self.restart_button.rect.topleft = (530, 580)
            self.levels_button = MenuButton('menu', game_end_menu_button_group)
            self.levels_button.rect.topleft = (390, 580)
        time_now = get_ticks()
        if time_now - self.last_animation >= 30:
            self.image.blit(self.original_image, (0, 0))
            if self.image_num < 8:
                now_im = GameEndMenu.star_images[self.image_num]
                if result < 0:
                    self.image.blit(grayscale(now_im), (150 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                else:
                    self.image.blit(now_im, (150 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                self.image_num += 1
                self.last_animation = get_ticks()
            elif self.image_num < 17:
                now_im = GameEndMenu.star_images[self.image_num - 9]
                if result < 1:
                    self.image.blit(grayscale(now_im), (450 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                else:
                    self.image.blit(now_im, (450 - now_im.get_width() // 2, 120 - now_im.get_height() // 2))
                self.image_num += 1
                self.last_animation = get_ticks()
            elif self.image_num < 26:
                now_im = GameEndMenu.star_images[self.image_num - 18]
                if result < 2:
                    self.image.blit(grayscale(now_im), (300 - now_im.get_width() // 2, 90 - now_im.get_height() // 2))
                else:
                    self.image.blit(now_im, (300 - now_im.get_width() // 2, 90 - now_im.get_height() // 2))
                self.image_num += 1
                self.last_animation = get_ticks()
            if self.image_num < 37 and result == 3 and time_now - self.last_animation >= 200:
                now_im = GameEndMenu.perf_image
                self.alpha_now += 25
                now_im.set_alpha(self.alpha_now)
                self.image.blit(now_im, (225, 165))
                self.image_num += 1
            if self.image_num == 8 or self.image_num == 17 or self.image_num == 26 or self.image_num == 37:
                self.original_image.blit(self.image, (0, 0))
                self.image_num += 1

            to_menu = False
            for button in game_end_menu_button_group:
                    if button.rect.collidepoint(mouse.get_pos()):
                        button.image.blit(button.select_image, (0, 0))
                        if mouse.get_pressed()[0]:
                            if button.type == 'menu':
                                raise QuitError
                    else:
                        button.image.blit(button.unselect_image, (0, 0))


