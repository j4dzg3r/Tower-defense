from pygame import init as pginit
from pygame import sprite
from pygame import display
from pygame import time
from pygame import event as pgevent
from pygame import mouse
from pygame import QUIT, MOUSEBUTTONUP


pginit()

size = width, height = 1110, 960
screen = pygame.display.set_mode(size)
weapon_group = pygame.sprite.Group()
foundation_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
health_bar_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()
gate_group = pygame.sprite.Group()

clock = time.Clock()


from typing import Optional

from subpackages.map import Map
from subpackages.game_menus.game_menu import GameMenu
from subpackages.errors import QuitError


def main():
    running = True

    game_menu = GameMenu()

    in_game = False

    while running:
        try:
            in_game, level_path = game_menu.update(screen)
            if in_game:
                print(level_path)
                map = Map(level_path, weapon_group, foundation_group, enemy_group, health_bar_group)
        except QuitError:
            running = False
        else:
            while in_game:
                screen.fill("green")
                for event in pgevent.get():
                    if event.type == QUIT:
                        in_game = False
                        game_menu.to_game_menu()
                    if event.type == MOUSEBUTTONUP and event.button == 1:
                        mouse_pos = mouse.get_pos()
                        map.process_click(mouse_pos, weapon_group, foundation_group, missile_group)

                map.render(screen)
                enemy_group.update()
                enemy_group.draw(screen)

                missile_group.update(enemy_group)
                missile_group.draw(screen)

                gate_group.update(screen, enemy_group)

                health_bar_group.draw(screen)
                
                weapon_group.update(screen, enemy_group)
                foundation_group.draw(screen)
                weapon_group.draw(screen)
                display.flip()
                clock.tick(60)
        display.flip()
        clock.tick(50)


if __name__ == '__main__':
    main()
