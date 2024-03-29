import pygame.time
import pytmx
import xml.etree.ElementTree as ET
from sqlite3 import Connection

from pygame import display
from pygame import Surface
from pygame.sprite import Group

from .game_menus.shopping_menu import ShoppingMenu

from typing import Tuple

from . import towers
from .enemy import Enemy
from .gates import Gate


class Map:
    def __init__(self, path_to_level: str, level_num: int, conn: Connection, *groups: Group) -> None:
        self.conn = conn

        with open(path_to_level) as level:
            parsed_level = level.readlines()
            self.map = pytmx.load_pygame(parsed_level[0].rstrip())

            xml_parser = ET.parse(parsed_level[0].rstrip()).getroot()
            polyline_obj = xml_parser.find("objectgroup").find("object")
            start_coords = tuple(list(map(lambda x: int(x[1]), polyline_obj.items()))[1:])
            self.way_points = list(
                map(
                    lambda x: tuple(x[0] + x[1] for x in zip(tuple(map(int, x.split(','))), start_coords)),
                    polyline_obj.find("polyline").items()[0][1].split()
                )
            )

            self.free_tiles = list(map(int, parsed_level[1].split()))
            self.waves = parsed_level[2].split('; ')
            with open(parsed_level[0].rstrip()) as map_tmx:
                parsed_map = map_tmx.readlines()
                self.gates = [((int(parsed_map[14].rstrip().split('"')[3]), int(parsed_map[14].rstrip().split('"')[5])),
                               int(parsed_map[16].rstrip().split('"')[5])),
                              ((int(parsed_map[20].rstrip().split('"')[3]), int(parsed_map[20].rstrip().split('"')[5])),
                               int(parsed_map[22].rstrip().split('"')[5])),
                              ((int(parsed_map[26].rstrip().split('"')[3]), int(parsed_map[26].rstrip().split('"')[5])),
                               int(parsed_map[28].rstrip().split('"')[5]))]

        self.cur_wave = 0
        self.groups_in_wave = list(map(lambda x: list(map(int, x.split(' * '))), self.waves[self.cur_wave].split(', ')))
        self.cur_group = 0
        self.spawn_in_group = 0
        self.time_last_spawn = -1
        self.spawn_delay = 800
        self.group_delay = 1500
        self.waves_delay = 4000
        self.time_to_wait = self.spawn_delay
        self.level_num = level_num
        self.level_finished = False
        self.result_saved = False
        self.score = 3
        self.lost = False

        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.shopping_list = ShoppingMenu()
        self.weapon_group, self.foundation_group, self.enemy_group, self.health_bar_group, self.gate_group = groups
        display.set_mode((self.tile_size * self.width + 150, self.tile_size * self.width))

        for i in range(3):
            Gate(self.gates[i][0], self.gates[i][1], self.gate_group)

    def render(self, screen: Surface) -> None:
        time_now = pygame.time.get_ticks()
        if not self.level_finished:
            for enemy in self.enemy_group:
                if enemy.pos == self.way_points[-1]:
                    self.level_finished = True
                    self.lost = True
            if self.time_to_wait == 0:
                if len(self.enemy_group) == 0:
                    self.cur_wave += 1
                    if self.cur_wave == len(self.waves):
                        self.level_finished = True
                    else:
                        self.time_to_wait = self.waves_delay
                        self.groups_in_wave = list(
                            map(lambda x: list(map(int, x.split(' * '))), self.waves[self.cur_wave].split(', ')))
                        self.time_last_spawn = time_now

            elif self.cur_wave < len(self.waves) and time_now - self.time_last_spawn >= self.time_to_wait:
                self.time_to_wait = self.spawn_delay
                self.time_last_spawn = time_now
                self.spawn_in_group += 1
                Enemy(self.way_points, self.enemy_group, self.health_bar_group)

                if self.spawn_in_group == self.groups_in_wave[self.cur_group][0]:
                    self.spawn_in_group = 0
                    self.cur_group += 1
                    self.time_to_wait = self.group_delay

                if self.cur_group == len(self.groups_in_wave):
                    self.cur_group = 0
                    self.time_to_wait = 0

        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))
        if not self.level_finished:
            self.shopping_list.draw(screen)

        self.score = len(self.gate_group) - self.lost

        if self.level_finished and not self.result_saved:
            win = not self.lost
            gates = len(self.gate_group)
            stars = gates + win
            if stars > 3:
                stars = 3

            self.conn.cursor().execute(
                """
                INSERT INTO levelsResults(level_number, stars) VALUES(?, ?)
                """,
                (self.level_num, stars)
            )
            self.conn.commit()

            self.result_saved = True

    def get_tile_id(self, position: Tuple[int, int]) -> int:
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def process_click(self, cursor_pos: Tuple[int, int], *groups: Group) -> None:
        if self.shopping_list.get_selected_item() != '':
            self.set_tower(self.shopping_list.get_selected_item(), cursor_pos, *groups)

    def set_tower(self, tower: str, coords: Tuple[int, int], *groups: Group) -> None:
        cell = coords[0] // self.tile_size, coords[1] // self.tile_size
        if cell not in [tuple(map(lambda x: x // 64, i.rect.topleft)) for i in self.foundation_group] and 0 <= cell[
            0] < self.width and 0 <= cell[1] < self.height:
            if self.get_tile_id(cell) in self.free_tiles:
                if tower == "Pukalka":
                    if self.shopping_list.create_transaction():
                        towers.Pukalka((cell[0] * self.tile_size, cell[1] * self.tile_size),
                                       self.shopping_list.price["Pukalka"], *groups)

    def kaput(self) -> None:
        self.shopping_list.refresh()
