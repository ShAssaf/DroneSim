
from src.environment.pygame_handler import PygameHandler
from src.utils.util_classes import InternalGPS, ThreeDVector
from src.environment.drones_server import DroneServer


class Environment:
    def __init__(self):
        self.drones_server = DroneServer()
        self.drones_server.start_server()
        self.pygame_handler = PygameHandler(self.drones_server.clients)


def main():
    pg = Environment()
    pg.drones = pg.pygame_handler.start_simulation()


if __name__ == "__main__":
    main()
