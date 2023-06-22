import multiprocessing
import pickle
import socket

from src.drone.Drone import SmallDrone
from src.utils.Consts import Consts
from src.utils.util_classes import InternalGPS, ThreeDVector


class DroneAgent:
    def __init__(self, name):
        self.drone = SmallDrone(name, InternalGPS(ThreeDVector(500, 500, 0)))
        self._socket_to_server = None
        self.connect_to_server()

    def connect_to_server(self):
        self._socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_to_server.connect((Consts.HOST, Consts.PORT))
        process = multiprocessing.Process(target=self.communicate_with_server)

        # Start the process
        process.start()

    def communicate_with_server(self):
        while True:
            data = self._socket_to_server.recv(1024).decode()
            if data == "get_location":
                # Serialize the object
                serialized_data = pickle.dumps(self.drone.get_gps())
                # Send the serialized object
                self._socket_to_server.sendall(serialized_data)
            elif data == "get_velocity":
                # Serialize the object
                serialized_data = pickle.dumps(self.drone.gps.get_velocity())
                # Send the serialized object
                self._socket_to_server.sendall(serialized_data)
            elif data == "get_battery_status":
                serialized_data = pickle.dumps(self.drone.power_controller.get_battery_percentage())
                self._socket_to_server.sendall(serialized_data)
            elif data == "get_drone_name":
                serialized_data = pickle.dumps(self.drone.name)
                self._socket_to_server.sendall(serialized_data)
            elif data.startswith("accelerate"):
                self.drone.motion_controller.accelerate(data.split(":")[1], data.split(" ")[2], data.split(" ")[3])
            elif data == "update":
                self.drone.calculate_gps()
                self.drone.power_controller.calculate_battery(self.drone.get_speed())
