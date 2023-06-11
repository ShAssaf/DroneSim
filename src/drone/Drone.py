from typing import Type
from src.drone.power_management import BatteryController
from src.drone.motion_controller import MotionControl
from src.utils.Consts import Consts, SmallDroneDefaults
from src.utils.util_classes import InternalGPS, debug_print


class Drone:
    def __init__(self, name, battery, max_speed, max_vertical_speed, max_height, max_distance, gps=Type[InternalGPS],
                 size=Consts.BigDroneSize):
        self.name = name
        self.gps = InternalGPS() if gps is None else gps
        self.battery = battery
        self.size = size
        self.max_speed = max_speed
        self.max_vertical_speed = max_vertical_speed
        self.max_height = max_height
        self.max_distance = max_distance  # Todo: I think we can remove this one (Shlomo)
        self.motion_controller = MotionControl(self)
        self.power_controller = BatteryController()

    def get_gps(self):
        return self.gps.get_gps()

    def set_gps(self, x, y, z):
        self.gps.set_gps(x, y, z)

    def get_speed(self):
        return self.gps.get_speed()

    def set_speed(self, vel_x, vel_y, vel_z):
        self.gps.set_speed(min(vel_x, self.max_speed), min(vel_y, self.max_speed), min(vel_z, self.max_speed))

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def calculate_gps(self, dt=1):
        self.gps.calculate_position(dt)
        self.power_controller.calculate_battery(self.get_speed())
        if self.get_gps().z > self.max_height:
            debug_print("Drone reached max height")
        elif self.get_gps().z < 0:
            debug_print("Drone has crashed")


class SmallDrone(Drone):
    def __init__(self, name, gps=Type[InternalGPS]):
        super().__init__(name,
                         gps=gps,
                         battery=SmallDroneDefaults.BATTERY,
                         max_speed=SmallDroneDefaults.MAX_SPEED,
                         max_height=SmallDroneDefaults.MAX_HEIGHT,
                         max_vertical_speed=SmallDroneDefaults.MAX_VERTICAL_SPEED,
                         max_distance=SmallDroneDefaults.MAX_DISTANCE)
