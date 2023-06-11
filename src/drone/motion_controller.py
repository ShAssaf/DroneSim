from src.utils.util_classes import ThreeDVector, debug_print

class MotionControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.max_vertical_speed = vehicle.max_vertical_speed
        self.max_total_speed = vehicle.max_speed

    def accelerate(self, x, y, z):
        if ThreeDVector(self.vehicle.get_speed().x + x, self.vehicle.get_speed().y + y, self.vehicle.get_speed().z + z)\
                .get_magnitude() < self.max_total_speed and abs(
                self.vehicle.get_speed().z + z) < self.max_vertical_speed:
            self.vehicle.set_speed(self.vehicle.get_speed().x + x, self.vehicle.get_speed().y + y,
                                   self.vehicle.get_speed().z + z)
        else:
            debug_print("Drone reached max speed")
