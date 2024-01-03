import os
import sys
import random
import math

import pygame
from pygame.math import Vector2

from .functions import load_image


path_w = 50


class Enemy(pygame.sprite.Sprite):
    image = original_image = load_image("enemies/towerDefense_tile245.png")

    def __init__(self, way_points, *groups):
        super().__init__(*groups)
        self.waypoints = way_points
        self.target_waypoint = 1
        self.pos = Vector2(self.waypoints[0])
        self.speed = 2

        self.angle = self.find_angle(self.target_waypoint)
        self.in_rotation = False
        self.rotation_angle = 0
        self.direction = 0
        self.rotation_values()

        self.original_image = Enemy.original_image
        self.image = pygame.transform.rotate(self.original_image, -self.angle - 90 * self.direction)
        self.rect = self.image.get_rect()
        self.rect.centery = self.pos[1]

    def find_angle(self, cur_wp):
        prev, curr, next = self.waypoints[cur_wp - 1], self.waypoints[cur_wp], self.waypoints[cur_wp + 1]
        if next[0] < prev[0] and next[0] < curr[0]:
            return 0
        if next[1] < prev[1] and next[1] < curr[1]:
            return 90
        if next[0] > prev[0] and next[0] > curr[0]:
            return 180
        if next[1] > prev[1] and next[1] > curr[1]:
            return 270

        # fv = Vector2(self.waypoints[cur_wp][0] - self.waypoints[cur_wp - 1][0],
        #              self.waypoints[cur_wp][1] - self.waypoints[cur_wp - 1][1])
        # sv = Vector2(self.waypoints[cur_wp + 1][0] - self.waypoints[cur_wp][0],
        #              self.waypoints[cur_wp + 1][1] - self.waypoints[cur_wp][1])
        # return fv.angle_to(sv)

    def rotate_right(self, rad):
        if self.rotation_angle < 45:
            self.rect.centerx = rad * math.cos(math.radians(self.angle)) + self.rotation_x
            self.rect.centery = rad * math.sin(math.radians(self.angle)) + self.rotation_y
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90 * self.direction)
            self.angle = (self.angle + self.direction * 2) % 360

            self.rotation_angle = (self.rotation_angle + 1) % 360
        else:
            self.in_rotation = False
            # self.angle -= 1
            # print(-self.angle - 90 * self.direction, self.rotation_angle)
            self.image = pygame.transform.rotate(self.original_image, -self.angle - 90 * self.direction)
            self.rotation_angle = 0

            self.pos = (self.rect.centerx, self.rect.centery)

            self.target_waypoint += 1
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos

    def rotation_values(self):
        prev_wp = self.waypoints[self.target_waypoint - 1]
        this_wp = self.waypoints[self.target_waypoint]
        next_wp = self.waypoints[self.target_waypoint + 1]
        signs = ((next_wp[0] - prev_wp[0]) // abs(next_wp[0] - prev_wp[0]),
                 (next_wp[1] - prev_wp[1]) // abs(next_wp[1] - prev_wp[1]))
        clockw_signs = {(1, 1): (-1, 1), (1, -1): (1, 1), (-1, 1): (-1, -1), (-1, -1): (1, -1)}
        anticlockw_signs = {(1, 1): (1, -1), (1, -1): (-1, -1), (-1, 1): (1, 1), (-1, -1): (-1, 1)}
        cross_product = (prev_wp[0] - this_wp[0]) * (next_wp[1] - this_wp[1]) - \
                        (next_wp[0] - this_wp[0]) * (prev_wp[1] - this_wp[1])
        res_signs = anticlockw_signs[signs]

        if cross_product < 0:
            res_signs = clockw_signs[signs]
            if self.direction == -1:
                self.angle += 180
            self.direction = 1


        elif cross_product >= 0:
            res_signs = anticlockw_signs[signs]
            if self.direction == 1:
                self.angle += 180
            self.direction = -1

        self.rotation_x = this_wp[0] + path_w * res_signs[0]
        self.rotation_y = this_wp[1] + path_w * res_signs[1]

    def move(self):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.kill()

        dist = self.movement.length()
        if self.in_rotation:
            self.rotate_right(path_w)
        else:
            if dist >= self.speed:
                if self.target_waypoint < len(self.waypoints) - 1 and dist < path_w:
                    self.in_rotation = True
                    self.rotation_values()
                else:
                    self.pos += self.movement.normalize() * self.speed
            else:
                if dist:
                    self.pos += self.movement.normalize() * dist
                self.target_waypoint += 1

            self.rect.center = self.pos

    def update(self):
        self.move()
