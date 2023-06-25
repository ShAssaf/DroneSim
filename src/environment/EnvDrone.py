import pickle
import socket

import pygame

from src.utils.Consts import MapConsts, Consts
from src.utils.util_classes import ThreeDVector


class EnvDroneObj:
    def __init__(self, drone_socket: socket.socket):
        self.in_viewport = False
        self._socket = drone_socket
        self.last_location = ThreeDVector(0, 0, 0)
        self.last_velocity = ThreeDVector(0, 0, 0)

    def adjust_drone_color(self, height):
        if height < 0:
            self.color = ThreeDVector(0, 0, 0)
        else:
            self.color = ThreeDVector(255, 0, 0)
            if height > 255:
                self.color = ThreeDVector(255, 255, (height % 255))
            else:
                self.color = ThreeDVector(255, height, 0)

    def draw(self, screen, viewport_x, viewport_y, zoom_factor):
        if self.in_viewport:
            pygame.draw.circle(surface=screen, color=(self.color.r, self.color.g, self.color.b),
                               radius=Consts.SmallDroneSize,
                               center=(self.last_location.x * zoom_factor - viewport_x,
                                       self.last_location.y * zoom_factor - viewport_y))

    def check_in_viewport(self, viewport_x, viewport_y, zoom_factor):
        if viewport_x < self.last_location.x*zoom_factor < viewport_x + MapConsts. SCREEN_WIDTH \
                and viewport_y < self.last_location.y*zoom_factor < viewport_y + MapConsts.SCREEN_HEIGHT:
            self.in_viewport = True
        else:
            self.in_viewport = False

    def get_location(self):
        self._socket.sendall("get_location;".encode())
        # Receive the serialized object
        received_data = self._socket.recv(4096)
        # Deserialize the object
        deserialized_data = pickle.loads(received_data)  # show in terminal
        self.last_location = deserialized_data
        return deserialized_data

    def get_velocity(self):
        self._socket.sendall("get_velocity;".encode())
        # Receive the serialized object
        received_data = self._socket.recv(4096)
        # Deserialize the object
        deserialized_data = pickle.loads(received_data)
        return deserialized_data

    def get_battery_status(self):
        self._socket.sendall("get_battery_status;".encode())
        # Receive the serialized object
        received_data = self._socket.recv(4096)
        # Deserialize the object
        deserialized_data = pickle.loads(received_data)
        return deserialized_data

    def accelerate(self, x, y, z):
        self._socket.sendall(f"accelerate:{x},{y},{z};".encode())

    def update(self):
        self._socket.sendall(f"update;".encode())
