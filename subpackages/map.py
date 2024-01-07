import pygame.time
import pytmx
import xml.etree.ElementTree as ET

from pygame import display
from pygame import Surface
from pygame.sprite import Group

from .game_menus.shopping_menu import ShoppingMenu

from typing import Tuple, List

from . import towers
from .enemy import Enemy


class Map:
    def __init__(self, path_to_level: str, *groups: Group) -> None:
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

            self.num_enemies = int(parsed_level[1])
            self.free_tiles = list(map(int, parsed_level[2].split()))
            self.waves = parsed_level[3].split('; ')

        self.cur_wave = 0
        self.groups_in_wave = list(map(lambda x: list(map(int, x.split(' * '))), self.waves[self.cur_wave].split(', ')))
        self.cur_group = 0
        self.spawn_in_group = 0
        self.time_last_spawn = -1
        self.spawn_delay = 800
        self.group_delay = 1500
        self.waves_delay = 4000
        self.time_to_wait = self.spawn_delay
        self.level_finnished = False

        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.shopping_list = ShoppingMenu()
        self.weapon_group, self.foundation_group, self.enemy_group, self.health_bar_group = groups
        display.set_mode((self.tile_size * self.width + 150, self.tile_size * self.width))

    def render(self, screen: Surface) -> None:
        time_now = pygame.time.get_ticks()
        if not self.level_finnished:
            if self.time_to_wait == 0:
                if len(self.enemy_group) == 0:
                    self.cur_wave += 1
                    if self.cur_wave == len(self.waves):
                        self.level_finnished = True
                    else:
                        self.time_to_wait = self.waves_delay
                        self.groups_in_wave = list(
                            map(lambda x: list(map(int, x.split(' * '))), self.waves[self.cur_wave].split(', ')))
                        self.time_last_spawn = time_now
                        print('NEW WAVE', self.cur_wave, self.cur_group, self.spawn_in_group,
                              self.groups_in_wave[self.cur_group],
                              self.time_to_wait)

            elif self.cur_wave < len(
                    self.waves) and time_now - self.time_last_spawn >= self.time_to_wait:
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
                print(self.cur_wave, self.cur_group, self.spawn_in_group, self.groups_in_wave[self.cur_group],
                      self.time_to_wait)

        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))
        self.shopping_list.draw(screen)
        self.enemy_group.update()
        # if self.level_finnished:
        #     screen.fill((0, 255, 0), (200, 300, 700, 300))

    def get_tile_id(self, position: Tuple[int, int]) -> int:
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def process_click(self, cursor_pos: Tuple[int, int], *groups: Group) -> None:
        if self.shopping_list.get_selected_item() != '':
            self.set_tower(self.shopping_list.get_selected_item(), cursor_pos, *groups)

    def set_tower(self, tower: str, coords: Tuple[int, int], *groups: Group) -> None:
        cell = coords[0] // self.tile_size, coords[1] // self.tile_size
        if cell not in [tuple(map(lambda x: x // 64, i.rect.topleft)) for i in self.foundation_group] and 0 <= cell[0] < self.width and 0 <= cell[1] < self.height:
            if self.get_tile_id(cell) in self.free_tiles:
                if tower == "Pukalka":
                    if self.shopping_list.create_transaction():
                        towers.Pukalka((cell[0] * self.tile_size, cell[1] * self.tile_size), self.shopping_list.price["Pukalka"], *groups)
