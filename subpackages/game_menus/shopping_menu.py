from pygame import sprite
from pygame.sprite import Group
from pygame import Surface
from pygame import mouse
from pygame.font import Font

from typing import List, Dict

from ..functions import load_image


class PukalkaItem(sprite.Sprite):
    image = load_image("assets/shopping_menu_towers/Pukalka.png")
    price = 100.

    def __init__(self, *groups: Group) -> None:
        super().__init__(*groups)
        self.name = "Pukalka"
        self.image = PukalkaItem.image
        self.rect = self.image.get_rect()
        self.rect.center = 990, 100
        
        self.clicked = False
    
    def update(self, screen: Surface, selected_item: List[str]) -> None:
        self.draw_price(screen)
        mouse_pos = mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and mouse.get_pressed()[0] == 1:
            self.clicked = True
            selected_item[0] = self.name
        elif mouse.get_pressed()[0] == 0:
            self.clicked = False
            selected_item[0] = ""
        if self.clicked is True:
            screen.blit(self.image, (mouse_pos[0] - 32, mouse_pos[1] - 32))
    
    def draw_price(self, screen: Surface):
        screen.blit(Font(None, 40).render(f"{PukalkaItem.price:.2f}", True, (0, 0, 0)), (self.rect.centerx + 30, self.rect.centery - 10))


class ShoppingMenu():
    money = 300.

    def __init__(self) -> None:
        self.shopping_list = Group()
        self.price: Dict[str, float] = {}
        self.selected_item = [""]
        self.init_list()
    
    def init_list(self) -> None:
        PukalkaItem(self.shopping_list)
        for i in self.shopping_list:
            self.price[i.name] = i.price
    
    def draw(self, surface: Surface) -> None:
        self.draw_money(surface)
        self.shopping_list.draw(surface)
        self.shopping_list.update(surface, self.selected_item)
    
    def draw_money(self, surface: Surface):
        surface.blit(Font(None, 30).render(f"money: {ShoppingMenu.money:.2f}", True, (0, 0, 0)), (965, 10))
    
    def get_selected_item(self) -> str:
        return self.selected_item[0]
    
    def create_transaction(self) -> bool:
        if ShoppingMenu.money >= self.price[self.selected_item[0]]:
            self.transaction_accepted()
            return True
        return False

    def transaction_accepted(self) -> None:
        ShoppingMenu.money -= self.price[self.selected_item[0]]
        self.price[self.selected_item[0]] *= 1.1
        if self.selected_item[0] == "Pukalka":
            PukalkaItem.price *= 1.1
