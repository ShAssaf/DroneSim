import socket
import multiprocessing
from src.utils.Consts import Consts
from src.environment.EnvDrone import EnvDroneObj


class DroneServer:
    def __init__(self):
        manager = multiprocessing.Manager()
        self.clients = manager.list()
        self.clients_lock = manager.Lock()

    # Server process
    @staticmethod
    def server_process(clients,clients_lock):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Consts.HOST, Consts.PORT))
            print("Server started")
            s.listen()
            while True:
                conn, addr = s.accept()
                with clients_lock:
                    clients.append(EnvDroneObj(conn))
                    print('drones server :Connected by', addr)

    def start_server(self):
        s = multiprocessing.Process(target=self.server_process, args=(self.clients,self.clients_lock,))
        s.start()

