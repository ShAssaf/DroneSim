from src.drone.Drone import SmallDrone
from src.utils.util_classes import ThreeDVector, InternalGPS


class DroneControllerAgent:
    def __init__(self, name: str, target: ThreeDVector = ThreeDVector(200, 200, 0),
                 initial_position: ThreeDVector = ThreeDVector(500, 500, 0)):
        pass
        # self.drones_container = []
        # self.drone = SmallDrone(name, InternalGPS(initial_position))
        # self._socket_to_server = None
        # self.env = FakeEnv()
        # self.target = target
        # self.QAgent = QLearning()
        # self.out_of_map = False
        #
        # self.initial_position = initial_position
        # self.connect_to_server()
