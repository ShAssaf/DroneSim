import math
import os.path
import random
import time
from typing import Optional

from PIL import Image

from src.utils.Consts import DEBUG, Paths, MapConsts, Consts, NoiseConsts


class ThreeDVector:
    def __init__(self, x=0, y=0, z=0, threeDtuple=None):
        if threeDtuple is not None:
            x, y, z = threeDtuple
        self.coordinates = [x, y, z]
        self.x = self.coordinates[0]
        self.y = self.coordinates[1]
        self.z = self.coordinates[2]

    def __getitem__(self, index):
        return self.coordinates[index]

    def __setitem__(self, index, value):
        self.coordinates[index] = value

    def __sub__(self, other):
        if isinstance(other, ThreeDVector):
            x_diff = self.x - other.x
            y_diff = self.y - other.y
            z_diff = self.z - other.z
            return ThreeDVector(x_diff, y_diff, z_diff)
        else:
            raise TypeError(
                "Unsupported operand type. The '-' operator is supported between instances of ThreeDVector.")

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
        self.coordinates = [self.x, self.y, self.z]
        return (self.coordinates[0] ** 2 + self.coordinates[1] ** 2 + self.coordinates[2] ** 2) ** 0.5

    def get_angle(self):
        d = math.degrees(math.atan2(self.y, self.x)) + 90  # -self.y because the y axis is inverted
        if d < -180:
            d += 360
        if d > 180:
            d -= 360
        return d

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'z': self.z}

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    @staticmethod
    def y_x_z2x_y_z(coor):
        return [coor[1], coor[0], coor[2]]


class InternalGPS:
    def __init__(self, location: Optional[ThreeDVector] = None):
        self.time = time.time()
        self.location = ThreeDVector(0, 0, 0) if location is None else location
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
        if Consts.REAL_TIME:
            dt = time.time() - self.time
        else:
            dt = Consts.DT
        self.time = time.time()
        self.location.x += self.velocity.x * dt + random.gauss(NoiseConsts.MEAN, NoiseConsts.STD)
        self.location.y += self.velocity.y * dt + random.gauss(NoiseConsts.MEAN, NoiseConsts.STD)
        self.location.z += self.velocity.z * dt + random.gauss(NoiseConsts.MEAN, NoiseConsts.STD)

    def distance(self, other):
        return math.sqrt(
            (self.location.x - other[0]) ** 2 + (self.location.y - other[1]) ** 2 + (self.location.z - other[2]) ** 2)


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def change_map_scale(scale_factor):
    # Open the image file
    img = Image.open(MapConsts.MAP_PATH)
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


def create_scaled_maps():
    for i in [1, 2, 4, 8]:
        if os.path.exists(f'{Paths.TMP}/scaled_map_{i}.png'):
            continue
        print(f'Creating scaled map {i}')
        scale_factor = i
        # Open the image file
        img = Image.open(MapConsts.MAP_PATH)
        # Get the original dimensions of the image
        width, height = img.size

        # Calculate the new dimensions of the scaled image
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Resize the image using the new dimensions
        scaled_img = img.resize((new_width, new_height))

        # Save the scaled image to a file
        scaled_img.save(f'{Paths.TMP}/scaled_map_{i}.png')
