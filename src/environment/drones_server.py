import socket
import multiprocessing
import threading
from time import sleep


from src.utils.Consts import Consts
from src.environment.env_drone import EnvDroneObj


class DroneServer:
    def __init__(self):
        self.clients = []
        self.addresses = []
        self.start_server()

    # Server process
    @staticmethod
    def server_thread(clients):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Consts.HOST, Consts.PORT))
            print("Drone-Server started")
            s.listen()
            while True:
                conn, addr = s.accept()
                clients.append(EnvDroneObj(conn, addr))
                print('drones server :Connected by', addr)

    def start_server(self):
        s = threading.Thread(target=self.server_thread, args=(self.clients,))
        s.start()
        sleep(4)
