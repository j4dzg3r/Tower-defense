from pygame import sprite
from pygame.sprite import Group
from pygame import Surface
from pygame import mouse

from typing import List

from ..functions import load_image


class PukalkaItem(sprite.Sprite):
    image = load_image("assets/shopping_menu_towers/Pukalka.png")

    def __init__(self, *groups: Group) -> None:
        super().__init__(*groups)
        self.image = PukalkaItem.image
        self.rect = self.image.get_rect()
        self.rect.center = 1000, 100
        self.clicked = False
    
    def update(self, screen: Surface, selected_item: List[str]) -> None:
        mouse_pos = mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and mouse.get_pressed()[0] == 1:
            self.clicked = True
            selected_item[0] = "Pukalka"
        elif mouse.get_pressed()[0] == 0:
            self.clicked = False
            selected_item[0] = ""
        if self.clicked is True:
            screen.blit(self.image, (mouse_pos[0] - 32, mouse_pos[1] - 32))


class ShoppingMenu():
    def __init__(self) -> None:
        self.shopping_list = Group()
        self.money = 100
        self.price = {
            "Pukalka": 10
        }
        self.selected_item = [""]
        self.init_list()
    
    def init_list(self) -> None:
        PukalkaItem(self.shopping_list)
    
    def draw(self, surface: Surface) -> None:
        self.shopping_list.draw(surface)
        self.shopping_list.update(surface, self.selected_item)
    
    def get_selected_item(self) -> str:
        return self.selected_item[0]
    
    def transaction_accepted(self) -> None:
        self.money -= self.price[self.selected_item[0]]
