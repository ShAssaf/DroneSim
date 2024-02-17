import threading
import time
from typing import Type

from src.drone.misson_control import VehicleMissionControl, STATUS
from src.drone.motion_controller import MotionControl
from src.drone.power_management import BatteryController
from src.drone.radar import TwoDRadar
from src.environment.env_info_api import EnvironmentAPI
from src.utils.Consts import Consts, SmallDroneDefaults, RadarSpec
from src.utils.util_classes import InternalGPS, debug_print


class Drone:
    def __init__(self, name, max_speed, max_vertical_speed, max_height, gps=Type[InternalGPS],
                 size=Consts.BigDroneSize):
        self.name = name
        self.gps = InternalGPS() if gps is None else gps
        self.location = self.gps.get_gps()
        self.radar = TwoDRadar(r=RadarSpec.RANGE)
        self.size = size
        self.max_speed = max_speed
        self.max_vertical_speed = max_vertical_speed
        self.max_height = max_height
        self.motion_controller = MotionControl(self)
        self.mission_control = VehicleMissionControl(self)
        self.power_controller = BatteryController()
        self.env = None

        threading.Thread(target=self.update).start()  # init update thread

    def get_location(self):
        return self.gps.get_gps()

    def set_gps(self, x, y, z):
        self.gps.set_gps(x, y, z)

    def get_velocity(self):
        return self.gps.get_velocity()

    def set_velocity(self, vel_x, vel_y, vel_z):
        self.gps.set_speed(min(vel_x, self.max_speed), min(vel_y, self.max_speed), min(vel_z, self.max_speed))

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def calculate_gps(self):
        self.gps.calculate_position()
        if self.get_location().z > self.max_height:
            debug_print("Drone reached max height")
        elif self.get_location().z < 0:
            debug_print("Drone has crashed")

    def update(self):
        while True:
            time.sleep(1)
            self.calculate_gps()
            self.calculate_power_consumption()
            if self.mission_control.mission.mission_status == STATUS.IN_PROGRESS:
                self.mission_control.mission_step()
            self.env = EnvironmentAPI.get_env(self.get_location())
            self.radar.update_sense_circle(self.env, self.get_velocity().get_angle())

    def calculate_power_consumption(self):
        self.power_controller.calculate_battery(self.get_velocity())


class SmallDrone(Drone):
    def __init__(self, name, gps=Type[InternalGPS]):
        super().__init__(name,
                         gps=gps,
                         max_speed=SmallDroneDefaults.MAX_SPEED,
                         max_height=SmallDroneDefaults.MAX_HEIGHT,
                         max_vertical_speed=SmallDroneDefaults.MAX_VERTICAL_SPEED,
                         )
