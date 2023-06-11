from typing import Type

import pygame

from src.drone.Drone import Drone
from src.utils.Consts import SmallDroneDefaults, Consts, MapConsts
from src.utils.util_classes import InternalGPS, ThreeDVector


class DroneSimObj(Drone):
    def __init__(self, name, max_speed, max_vertical_speed, max_height, gps=Type[InternalGPS],
                 size=Consts.BigDroneSize):
        super().__init__(name, max_speed, max_vertical_speed, max_height, gps, size)
        self.in_viewport = False
        self.color = ThreeDVector(255, 0, 0)

    def adjust_drone_color(self, height):
        if height < 0 or height > self.max_height:
            self.color = ThreeDVector(0, 0, 0)
        else:
            self.color = ThreeDVector(255, 0, 0)
            if height > 255:
                self.color = ThreeDVector(255, 255, (height % 255))
            else:
                self.color = ThreeDVector(255, height, 0)

    def draw(self, screen, viewport_x, viewport_y):
        if self.in_viewport:
            pygame.draw.circle(surface=screen, color=(self.color.r, self.color.g, self.color.b), radius=self.size,
                               center=(self.gps.location.x - viewport_x, self.gps.location.y - viewport_y))

    def check_in_viewport(self, viewport_x, viewport_y):
        if viewport_x < self.gps.location.x < viewport_x + MapConsts.SCREEN_WIDTH \
                and viewport_y < self.gps.location.y < viewport_y + MapConsts.SCREEN_HEIGHT:
            self.in_viewport = True
        else:
            self.in_viewport = False


class SmallDroneSimObj(DroneSimObj):
    def __init__(self, name, gps=Type[InternalGPS]):
        super().__init__(name, max_speed=SmallDroneDefaults.MAX_SPEED,
                         max_height=SmallDroneDefaults.MAX_HEIGHT,
                         max_vertical_speed=SmallDroneDefaults.MAX_VERTICAL_SPEED,
                         gps=gps)
