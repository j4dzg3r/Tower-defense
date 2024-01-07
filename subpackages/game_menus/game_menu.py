from pygame import Surface
from pygame import Rect
from pygame import display
from pygame.font import Font
from pygame import event as pgevent
from pygame import mouse
from pygame import sprite
from pygame.draw import circle
from pygame import QUIT, MOUSEMOTION, MOUSEBUTTONUP, RESIZABLE

from typing import List, Tuple, Optional

from ..functions import load_image
from ..errors import QuitError


class ButtonToMainMenu():
    image = load_image("assets/game_menu/ToMenu.png")

    def __init__(self, coords: Tuple[int, int]) -> None:
        self.image = ButtonToMainMenu.image
        self.rect = self.image.get_rect()
        self.rect.topleft = coords


class GameMenu():
    fon = load_image("assets/game_menu/Preview_KenneyNL.png")

    def __init__(self) -> None:
        self.fon = GameMenu.fon
        self.fon.set_alpha(150)

        self.name_font = Font(None, 50)
        self.font = Font(None, 30)
        display.set_mode(self.fon.get_size(), RESIZABLE)

        self.game_name = self.name_font.render("Tower Defense", 1, "black")

        self.page_num = 0
        self.pages: List[List[List[str | int | Optional[Rect]]]] = [
            [
                ["Поехали!", "black", None],
                ["Правила игры", "black", None]
            ],
            [
                [1, "data/levels/level_1.txt", None],
                [2, "data/levels/level_2.txt", None]
            ]
        ]

        self.level_counter = 1

    def update(self, screen: Surface) -> Tuple[bool, str]:
        res = (False, "")

        screen.fill("white")
        screen.blit(self.fon, (0, 0))
        if self.page_num == 0:
            x, y = 50, 100
            screen.blit(self.game_name, self.game_name.get_rect(topleft=(x, y)))
            y = 200

            for i in self.pages[0]:
                text = self.font.render(i[0], 1, i[1])
                i[2] = text.get_rect(topleft=(x, y))
                screen.blit(text, i[2])
                y += 30

        elif self.page_num == 1:
            x, y = 100, 100
            for i, j in enumerate(self.pages[1]):
                color = ("red" if j[2] is not None and j[2].collidepoint(mouse.get_pos()) else "pink") \
                            if j[0] <= self.level_counter else "grey"
                rect = circle(screen, color, (x, y), 25)
                text = self.font.render(f"{j[0]}", 1, "black")
                screen.blit(text, text.get_rect(center=rect.center))
                j[2] = rect
                x += 60
                x = (i + 1) * 60 % 300 + 100
                y = (i + 1) * 60 // 400 + 100
        
        b_to_menu: Optional[ButtonToMainMenu] = None
        if self.page_num != 0:
            b_to_menu = ButtonToMainMenu((self.fon.get_width() - 150, 30))
            screen.blit(b_to_menu.image, (b_to_menu.rect))
        
        for event in pgevent.get():
            if event.type == QUIT:
                raise QuitError
            if event.type == MOUSEMOTION:
                if self.page_num == 0:
                    for i in self.pages[0]:
                        if i[2].collidepoint(mouse.get_pos()):
                            i[1] = "red"
                        else:
                            i[1] = "black"
                
            if event.type == MOUSEBUTTONUP:
                if b_to_menu and b_to_menu.rect.collidepoint(mouse.get_pos()):
                    self.page_num = 0
                if self.page_num == 0:
                    if self.pages[0][0][2].collidepoint(mouse.get_pos()):
                        self.page_num = 1
                elif self.page_num == 1:
                    for i in self.pages[1]:
                        if i[2].collidepoint(mouse.get_pos()):
                            if i[0] <= self.level_counter:
                                res = (True, i[1])
        
        return res

    def to_game_menu(self) -> None:
        display.set_mode(self.fon.get_size())
