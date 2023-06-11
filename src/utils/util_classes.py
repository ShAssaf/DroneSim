from typing import Optional
from src.utils.Consts import DEBUG


class ThreeDVector:
    def __init__(self, x=0, y=0, z=0):
        self.coords = [x, y, z]

    def __getitem__(self, index):
        return self.coords[index]

    def __setitem__(self, index, value):
        self.coords[index] = value

    def __getattr__(self, name):
        if name == 'x' or name == 'r':
            return self.coords[0]
        elif name == 'y' or name == 'g':
            return self.coords[1]
        elif name == 'z' or name == 'b':
            return self.coords[2]
        else:
            raise AttributeError(f"'ThreeDVector' object has no attribute '{name}'")

    def get_magnitude(self):
        return (self.coords[0] ** 2 + self.coords[1] ** 2 + self.coords[2] ** 2) ** 0.5


class InternalGPS:
    def __init__(self, location: Optional[ThreeDVector] = None):
        self.location = ThreeDVector() if location is None else location
        self.velocity = ThreeDVector(0, 0, 0)

    def get_gps(self):
        return self.location

    def set_gps(self, x, y, z):
        self.location.x = x
        self.location.y = y
        self.location.z = z

    def get_speed(self):
        return self.velocity

    def set_velx(self, velx):
        self.velocity.x = velx

    def set_vely(self, vely):
        self.velocity.y = vely

    def set_velz(self, velz):
        self.velocity.z = velz

    def set_speed(self, velx, vely, velz):
        self.set_velx(velx)
        self.set_vely(vely)
        self.set_velz(velz)

    def calculate_position(self, dt):
        self.location.x += self.velocity.x * dt
        self.location.y += self.velocity.y * dt
        self.location.z += self.velocity.z * dt


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)
