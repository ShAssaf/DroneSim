import time
from typing import Optional
from PIL import Image

from src.utils.Consts import DEBUG, Paths


class ThreeDVector:
    def __init__(self, x, y, z):
        self.coordinates = [x, y, z]
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, index):
        return self.coordinates[index]

    def __setitem__(self, index, value):
        self.coordinates[index] = value

    @property
    def r(self):
        return self.coordinates[0]

    @r.setter
    def r(self, value):
        self.coordinates[0] = value

    @property
    def g(self):
        return self.coordinates[1]

    @g.setter
    def g(self, value):
        self.coordinates[1] = value

    @property
    def b(self):
        return self.coordinates[2]

    @b.setter
    def b(self, value):
        self.coordinates[2] = value

    def get_magnitude(self):
        return (self.coordinates[0] ** 2 + self.coordinates[1] ** 2 + self.coordinates[2] ** 2) ** 0.5


class InternalGPS:
    def __init__(self, location: Optional[ThreeDVector] = None):
        self.time = time.time()
        self.location = ThreeDVector() if location is None else location
        self.initLocation = self.location
        self.velocity = ThreeDVector(0, 0, 0)

    def get_init_location(self):
        return self.initLocation

    def get_gps(self):
        return self.location

    def set_gps(self, x, y, z):
        self.location.x = x
        self.location.y = y
        self.location.z = z

    def get_velocity(self):
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

    def calculate_position(self):
        dt = time.time() - self.time
        self.time = time.time()
        self.location.x += self.velocity.x * dt
        self.location.y += self.velocity.y * dt
        self.location.z += self.velocity.z * dt


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def change_map_scale(scale_factor):
    # Open the image file
    img = Image.open(Paths.MAP_BG_PATH)
    # Get the original dimensions of the image
    width, height = img.size

    # Calculate the new dimensions of the scaled image
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize the image using the new dimensions
    scaled_img = img.resize((new_width, new_height))

    # Save the scaled image to a file
    scaled_img.save('/tmp/scaled_img.png')
    return '/tmp/scaled_map.png'
