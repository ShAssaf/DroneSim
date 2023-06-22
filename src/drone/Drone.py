from typing import Type
import time
from src.drone.power_management import BatteryController
from src.drone.motion_controller import MotionControl
from src.drone.radar import TwoDRadar
from src.utils.Consts import Consts, SmallDroneDefaults
from src.utils.util_classes import InternalGPS, debug_print


class Drone:
    def __init__(self, name, max_speed, max_vertical_speed, max_height, gps=Type[InternalGPS],
                 size=Consts.BigDroneSize):
        self.name = name
        self.gps = InternalGPS() if gps is None else gps
        self.radar = TwoDRadar(r=500)
        self.size = size
        self.max_speed = max_speed
        self.max_vertical_speed = max_vertical_speed
        self.max_height = max_height
        self.motion_controller = MotionControl(self)
        self.power_controller = BatteryController()

    def get_gps(self):
        return self.gps.get_gps()

    def set_gps(self, x, y, z):
        self.gps.set_gps(x, y, z)

    def get_speed(self):
        return self.gps.get_velocity()

    def set_speed(self, vel_x, vel_y, vel_z):
        self.gps.set_speed(min(vel_x, self.max_speed), min(vel_y, self.max_speed), min(vel_z, self.max_speed))

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def calculate_gps(self):
        self.gps.calculate_position()
        if self.get_gps().z > self.max_height:
            debug_print("Drone reached max height")
        elif self.get_gps().z < 0:
            debug_print("Drone has crashed")

    def calculate_power_consumption(self):
        self.power_controller.calculate_battery(self.get_speed())


class SmallDrone(Drone):
    def __init__(self, name, gps=Type[InternalGPS]):
        super().__init__(name,
                         gps=gps,
                         max_speed=SmallDroneDefaults.MAX_SPEED,
                         max_height=SmallDroneDefaults.MAX_HEIGHT,
                         max_vertical_speed=SmallDroneDefaults.MAX_VERTICAL_SPEED,
                         )
