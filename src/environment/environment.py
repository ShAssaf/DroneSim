from src.environment.DroneObj import SmallDroneSimObj
from src.environment.pygame_handler import PygameHandler
from src.utils.util_classes import InternalGPS, ThreeDVector


class Environment:
    def __init__(self, drones: list = None):
        self.drones = drones if drones is not None else [SmallDroneSimObj("drone0", gps=InternalGPS(ThreeDVector(1500, 1500, 0)))]
        self.pygame_handler = PygameHandler(self.drones)


def main():
    pg = Environment()
    pg.drones = pg.pygame_handler.start_simulation()


if __name__ == "__main__":
    main()
