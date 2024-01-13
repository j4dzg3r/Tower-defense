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

from os.path import exists
from os import mkdir
from sqlite3 import connect

from subpackages.map import Map
from subpackages.game_menus.game_menu import GameMenu
from subpackages.game_menus.game_end_menu import GameEndMenu
from subpackages.errors import QuitError


def main():
    if not exists("data/levels_results"):
        mkdir("data/levels_results")
    # if not exists("data/levels_results/results.csv"):
    #     with open("data/levels_results/results.csv", "w") as csvf:
    #         wr = writer(csvf, delimiter=';', quoting=QUOTE_MINIMAL)
    #         wr.writerow(["level_num", "date", "stars"])

    conn = connect("data/levels_results/results.db")
    if not conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        conn.cursor().execute(
            """
            CREATE TABLE levelsResults (
                id INTEGER PRIMARY KEY,
                level_number INTEGER NOT NULL,
                stars INTEGER NOT NULL
            );
            """
        )
        conn.commit()

    running = True

    game_menu = GameMenu(conn)

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
                game_end_menu_button_group = sprite.Group()

                map = Map(level_path,
                          int(level_path.split('/')[-1].split('.')[0].split('_')[1]),
                          conn,
                          weapon_group, foundation_group, enemy_group, health_bar_group, gate_group)
                game_end_menu = GameEndMenu(map.level_num)

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
                        for missile in missile_group:
                            missile.kill()
                        try:
                            gem_answer = game_end_menu.update(screen, map.score, game_end_menu_button_group)
                            if gem_answer == 'restart' or gem_answer == 'next':
                                map.kaput()
                                del map
                                game_end_menu.kill()

                                weapon_group = sprite.Group()
                                foundation_group = sprite.Group()
                                enemy_group = sprite.Group()
                                health_bar_group = sprite.Group()
                                missile_group = sprite.Group()
                                gate_group = sprite.Group()
                                game_end_menu_button_group = sprite.Group()
                                if gem_answer == 'next':
                                    print(level_path)
                                    level_path = level_path[:18] + str(int(level_path[18]) + 1) + level_path[19:]
                                    print(level_path)

                                map = Map(level_path, int(level_path.split('/')[-1].split('.')[0].split('_')[1]), conn,
                                          weapon_group, foundation_group, enemy_group, health_bar_group, gate_group)
                                game_end_menu = GameEndMenu(map.level_num)

                            screen.blit(game_end_menu.image, (255, 245))
                            game_end_menu_button_group.draw(screen)
                        except QuitError:
                            in_game = False
                            map.kaput()
                            del map
                            game_menu.to_game_menu()
                    display.flip()
                    clock.tick(60)
        display.flip()
        clock.tick(50)

    conn.close()


if __name__ == '__main__':
    main()
