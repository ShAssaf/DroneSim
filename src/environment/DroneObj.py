from typing import Type

import pygame

from src.drone.Drone import Drone
from src.utils.Consts import SmallDroneDefaults, Consts, MapConsts
from src.utils.util_classes import InternalGPS, ThreeDVector


class DroneSimObj(Drone):
    def __init__(self, name, battery, max_speed, max_vertical_speed, max_height, max_distance, gps=Type[InternalGPS],
                 size=Consts.BigDroneSize):
        super().__init__(name, battery, max_speed, max_vertical_speed, max_height, max_distance, gps, size)
        self.in_viewport = False
        self.color = ThreeDVector(255, 0, 0)

    def draw(self, screen, viewport_x, viewport_y):
        if self.in_viewport:
            #todo: modify drone color according to highgt
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
        super().__init__(name, battery=SmallDroneDefaults.BATTERY,
                         max_speed=SmallDroneDefaults.MAX_SPEED,
                         max_height=SmallDroneDefaults.MAX_HEIGHT,
                         max_distance=SmallDroneDefaults.MAX_DISTANCE,
                         max_vertical_speed=SmallDroneDefaults.MAX_VERTICAL_SPEED,
                         gps=gps)
