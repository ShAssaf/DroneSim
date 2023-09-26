import socket
import multiprocessing
import threading
from time import sleep


from src.utils.Consts import Consts
from src.environment.EnvDrone import EnvDroneObj


class DroneServer:
    def __init__(self):
        self.clients = []
        self.addresses = []

    # Server process
    @staticmethod
    def server_thread(clients):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Consts.HOST, Consts.PORT))
            print("Server started")
            s.listen()
            while True:
                conn, addr = s.accept()
                clients.append(EnvDroneObj(conn, addr))

                # if len(clients) == 1:
                #     clients[0].start_learning()
                print('drones server :Connected by', addr)

    def start_server(self):
        s = threading.Thread(target=self.server_thread, args=(self.clients,))
        s.start()
        sleep(4)


