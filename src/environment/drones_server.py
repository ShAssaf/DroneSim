import socket
import multiprocessing
from src.utils.Consts import Consts
from src.environment.DroneObj import DroneSimObj


class DroneServer:
    def __init__(self):
        manager = multiprocessing.Manager()
        self.clients = manager.list()

    # Server process
    @staticmethod
    def server_process(clients):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Consts.HOST, Consts.PORT))
            print("Server started")
            s.listen()
            while True:
                conn, addr = s.accept()
                clients.append(DroneSimObj(conn))
                print('drones server :Connected by', addr)

    def start_server(self):
        s = multiprocessing.Process(target=self.server_process, args=(self.clients,))
        s.start()

