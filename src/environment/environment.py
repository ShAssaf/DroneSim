import multiprocessing
import traceback
from time import sleep

from src.environment.drones_server import DroneServer
from src.environment.pygame_handler import PygameHandler


class Environment:
    def __init__(self):
        self.drones_server = DroneServer()
        self.drones_server.start_server()
        self.update_drones(self.drones_server.clients,self.drones_server.clients_lock)
        self.pygame_handler = PygameHandler(self.drones_server.clients)

    @staticmethod
    def update_drones_data(clients,clients_lock):
        while True:
            with clients_lock:
                try:
                    for idx in range(len(clients)):
                        sleep(1)
                        drone = clients[idx]
                        drone.update()
                        drone.get_location()
                        drone.get_velocity()
                        clients[idx] = drone
                except Exception as e:
                    print(e)


    @staticmethod
    def update_drones(clients,clients_lock):
        s = multiprocessing.Process(target=Environment.update_drones_data, args=(clients,clients_lock,))
        s.start()


def main():
    pg = Environment()
    pg.drones = pg.pygame_handler.start_simulation()


if __name__ == "__main__":
    main()
