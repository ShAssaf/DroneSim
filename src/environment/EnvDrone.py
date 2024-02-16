import pickle
import socket

from src.utils.Consts import MapConsts
from src.utils.util_classes import ThreeDVector


class EnvDroneObj:
    def __init__(self, drone_socket: socket.socket, physical_drone_address):
        self.color = None
        self.in_viewport = False
        self._socket = drone_socket
        self.address = physical_drone_address
        self.last_location = ThreeDVector(0, 0, 0)
        self.last_velocity = ThreeDVector(0, 0, 0)
        self.target_location = ThreeDVector(0, 0, 0)
        self.last_battery_status = 100
        self.is_learning = False

    def adjust_drone_color(self, height):
        if height < 0:
            self.color = ThreeDVector(0, 0, 0)
        else:
            self.color = ThreeDVector(255, 0, 0)
            if height > 255:
                self.color = ThreeDVector(255, 255, (height % 255))
            else:
                self.color = ThreeDVector(255, min(height * 3, 255), 0)

    def check_in_viewport(self, viewport_x, viewport_y, zoom_factor):
        if viewport_x < self.last_location.x * zoom_factor < viewport_x + MapConsts.SCREEN_WIDTH \
                and viewport_y < self.last_location.y * zoom_factor < viewport_y + MapConsts.SCREEN_HEIGHT:
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
        self.last_velocity = deserialized_data
        return deserialized_data

    def get_battery_status(self):
        self._socket.sendall("get_battery_status;".encode())
        # Receive the serialized object
        received_data = self._socket.recv(4096)
        # Deserialize the object
        deserialized_data = pickle.loads(received_data)
        self.last_battery_status = deserialized_data
        return deserialized_data

    def accelerate(self, x, y, z):
        try:
            self._socket.sendall(f"accelerate:{x},{y},{z};".encode())
        except Exception as e:
            print(e)
            self.accelerate(x, y, z)

    def start_learning(self):
        self._socket.sendall("start_learning;".encode())
        self.is_learning = True

    def get_target_vector(self):
        self._socket.sendall("get_target_vector;".encode())
        # Receive the serialized object
        received_data = self._socket.recv(4096)
        # Deserialize the object
        deserialized_data = pickle.loads(received_data)
        self.target_location = deserialized_data
        return deserialized_data

    def set_imitate(self, action):
        self._socket.sendall(f"set_imitate:{action};".encode())

    def accelerate2(self, direction=0):
        self._socket.sendall(f"accelerate2:{direction};".encode())

    def turn_to(self, direction=0):
        self._socket.sendall(f"turn_to:{direction};".encode())
