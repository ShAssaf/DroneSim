import math

from src.utils.logger import get_logger
from src.utils.util_classes import ThreeDVector, debug_print

logger = get_logger(__name__)
class MotionControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.max_vertical_speed = vehicle.max_vertical_speed
        self.max_total_speed = vehicle.max_speed

    def accelerate(self, x, y, z):
        if ThreeDVector(self.vehicle.get_velocity().x + x, self.vehicle.get_velocity().y + y,
                        self.vehicle.get_velocity().z + z) \
                .get_magnitude() < self.max_total_speed and abs(
            self.vehicle.get_velocity().z + z) < self.max_vertical_speed:
            vel = self.vehicle.get_velocity()
            self.vehicle.set_velocity(vel.x + x, vel.y + y, vel.z + z)
        else:
            debug_print("Drone reached max speed")

    def turn_to(self, direction=0):
        velocity = self.vehicle.get_velocity()
        vel_mag = velocity.get_magnitude()
        angel = velocity.get_angle()
        if direction == 0:
            angel += 36
            if angel > 180:
                angel -= 360
        else:
            angel -= 36
            if angel < -180:
                angel += 360
        self.vehicle.set_velocity(vel_mag * math.sin(math.radians(angel)), vel_mag * -math.cos(math.radians(angel)),
                                  velocity.z)

    def accelerate2(self, direction=0):
        velocity = self.vehicle.get_velocity()
        vel_mag = velocity.get_magnitude()
        vel_dir = velocity.get_angle()
        if direction == 0:
            if vel_mag < self.max_total_speed:
                vel_mag += 1
        else:
            if vel_mag >= 1:
                vel_mag -= 1
        self.vehicle.set_velocity(vel_mag * math.sin(math.radians(vel_dir)), vel_mag * -math.cos(math.radians(vel_dir)),
                                  velocity.z)

    def go_to_point(self, target):  # y x z
        logger.info(f"{self.vehicle.name}: Going to point {target}")
        """get a 3dd point and adapt the drone velocity to go to that point"""
        dx, dy, dz = target[0] - self.vehicle.get_location().x, target[1] - self.vehicle.get_location().y, \
            target[2] - self.vehicle.get_location().z
        v_mag = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        if v_mag > 0:
            self.vehicle.set_velocity((dx / v_mag) * self.vehicle.max_speed, (dy / v_mag) * self.vehicle.max_speed,
                                      (dz / v_mag) * self.vehicle.max_speed)

    def stop(self):
        self.vehicle.set_velocity(0, 0, 0)
