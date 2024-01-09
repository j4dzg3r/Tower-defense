from pygame import init as pginit
from pygame import sprite
from pygame import display
from pygame import time
from pygame import event as pgevent
from pygame import mouse
from pygame import QUIT, MOUSEBUTTONUP


pginit()

size = width, height = 1110, 960
screen = display.set_mode(size)
clock = time.Clock()

from typing import Optional

from subpackages.map import Map
from subpackages.game_menus.game_menu import GameMenu
from subpackages.game_menus.game_end_menu import GameEndMenu
from subpackages.errors import QuitError


def main():
    running = True

    game_menu = GameMenu()

    in_game = False

    while running:
        try:
            in_game, level_path = game_menu.update(screen)
            if in_game:
                weapon_group = sprite.Group()
                foundation_group = sprite.Group()
                enemy_group = sprite.Group()
                health_bar_group = sprite.Group()
                missile_group = sprite.Group()
                gate_group = sprite.Group()

                map = Map(level_path, weapon_group, foundation_group, enemy_group, health_bar_group, gate_group)
                game_end_menu = GameEndMenu()

        except QuitError:
            running = False
        else:
            while in_game:
                screen.fill("green")
                for event in pgevent.get():
                    if event.type == QUIT:
                        in_game = False
                        map.kaput()
                        del map
                        game_menu.to_game_menu()
                        break
                    if event.type == MOUSEBUTTONUP and event.button == 1:
                        mouse_pos = mouse.get_pos()
                        map.process_click(mouse_pos, weapon_group, foundation_group, missile_group)
                else:
                    map.render(screen)
                    if not map.level_finished:
                        enemy_group.update()
                        gate_group.update(enemy_group)
                        missile_group.update(enemy_group)
                        weapon_group.update(screen, enemy_group)
                    enemy_group.draw(screen)
                    missile_group.draw(screen)
                    health_bar_group.draw(screen)
                    foundation_group.draw(screen)
                    weapon_group.draw(screen)
                    gate_group.draw(screen)
                    if map.level_finished:
                        game_end_menu.update(screen, len(gate_group) - map.lost)
                        screen.blit(game_end_menu.image, (255, 245))
                    display.flip()
                    clock.tick(60)
        display.flip()
        clock.tick(50)


if __name__ == '__main__':
    main()
