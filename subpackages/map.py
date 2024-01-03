import pytmx
import xml.etree.ElementTree as ET

from pygame import Surface
from pygame.sprite import Group

from .game_menus.shopping_menu import ShoppingMenu

from typing import Tuple

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
            self.road_tiles = list(map(int, parsed_level[2].split()))
            self.free_tiles = list(map(int, parsed_level[3].split()))
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.shopping_list = ShoppingMenu()
        self.weapon_group, self.foundation_group, self.enemy_group, self.health_bar_group = groups
        Enemy(self.way_points, self.enemy_group, self.health_bar_group)
    
    def render(self, screen: Surface) -> None:
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))
        
        self.shopping_list.draw(screen)
        self.enemy_group.update()
    
    def get_tile_id(self, position: Tuple[int, int]) -> int:
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]
    
    def process_click(self, cursor_pos: Tuple[int, int], *groups: Group) -> None:
        if self.shopping_list.get_selected_item() != '':
            self.set_tower(self.shopping_list.get_selected_item(), cursor_pos, *groups)

    def set_tower(self, tower: str, coords: Tuple[int, int], *groups: Group) -> None:
        cell = coords[0] // self.tile_size, coords[1] // self.tile_size
        if 0 <= cell[0] <= self.width and 0 <= cell[1] <= self.height:
            if self.get_tile_id(cell) in self.free_tiles:
                if tower == "Pukalka":
                    towers.Pukalka((cell[0] * self.tile_size, cell[1] * self.tile_size), *groups)
                self.shopping_list.transaction_accepted()
