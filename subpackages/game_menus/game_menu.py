from pygame import Surface
from pygame import Rect
from pygame import display
from pygame.font import Font
from pygame import event as pgevent
from pygame import mouse
from pygame import sprite
from pygame.draw import circle
from pygame import QUIT, MOUSEMOTION, MOUSEBUTTONUP, RESIZABLE

from sqlite3 import connect, Connection

from typing import List, Tuple, Optional

from ..functions import load_image
from ..errors import QuitError


class ButtonToMainMenu():
    image = load_image("assets/game_menu/ToMenu.png")

    def __init__(self, coords: Tuple[int, int]) -> None:
        self.image = ButtonToMainMenu.image
        self.rect = self.image.get_rect()
        self.rect.topleft = coords
        self.is_shown = False

    def update(self, screen: Surface) -> None:
        if self.is_shown:
            screen.blit(self.image, self.rect)


class GameMenu():
    fon = load_image("assets/game_menu/Preview_KenneyNL.png")

    def __init__(self, conn: Connection) -> None:
        self.conn = conn

        self.fon = GameMenu.fon
        self.fon.set_alpha(150)

        self.name_font = Font(None, 50)
        self.font = Font(None, 30)
        self.small_font = Font(None, 20)
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
                [2, "data/levels/level_2.txt", None],
                [3, "data/levels/level_3.txt", None]
            ]
        ]

        self.level_counter = 1
        self.b_to_menu = ButtonToMainMenu((self.fon.get_width() - 150, 30))

    def update(self, screen: Surface) -> Tuple[bool, str]:
        screen.fill("white")
        screen.blit(self.fon, (0, 0))

        self.b_to_menu.update(screen)

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
            cur = self.conn.cursor()

            x, y = 100, 100
            for i, j in enumerate(self.pages[1]):
                res = cur.execute(
                    """
                    SELECT MAX(stars) FROM levelsResults WHERE level_number = ?
                    """,
                    (j[0],)
                ).fetchone()
                stars = ""
                if res[0] and res[0] > 0:
                    self.level_counter = i + 2
                    stars = f"stars: {res[0]}"
                color = ("red" if j[2] is not None and j[2].collidepoint(mouse.get_pos()) else "pink") \
                    if j[0] <= self.level_counter else "grey"
                rect = circle(screen, color, (x, y), 25)
                text = self.font.render(f"{j[0]}", 1, "black")
                screen.blit(text, text.get_rect(center=rect.center))
                j[2] = rect
                screen.blit(self.small_font.render(stars, 1, "black"), (x - 23, y + 26))
                x += 60
                x = (i + 1) * 60 % 300 + 100
                y = (i + 1) * 60 // 400 + 100

        if self.page_num != 0:
            self.b_to_menu.is_shown = True
        else:
            self.b_to_menu.is_shown = False

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
                if self.b_to_menu.is_shown and self.b_to_menu.rect.collidepoint(mouse.get_pos()):
                    self.page_num = 0
                if self.page_num == 0:
                    if self.pages[0][0][2].collidepoint(mouse.get_pos()):
                        self.page_num = 1
                elif self.page_num == 1:
                    for i in self.pages[1]:
                        if i[2].collidepoint(mouse.get_pos()):
                            if i[0] <= self.level_counter:
                                return True, i[1]

        return False, ""

    def to_game_menu(self) -> None:
        display.set_mode(self.fon.get_size())
