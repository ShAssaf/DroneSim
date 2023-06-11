from src.environment.DroneObj import SmallDroneSimObj
from src.environment.pygame_handler import PygameHandler
from src.utils.util_classes import InternalGPS


class Environment:
    def __init__(self, drones: list = None):
        self.drones = drones if drones is not None else [SmallDroneSimObj("drone0", gps=InternalGPS())]
        self.pygame_handler = PygameHandler()


def main():
    pg = Environment()
    pg.drones = pg.pygame_handler.start_simulation(pg.drones)


if __name__ == "__main__":
    main()
