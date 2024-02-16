import pickle

from src.RL.drone_agent_q_learning import DroneAgent
from src.drone.misson_control import MissionControl, Mission
from src.environment.drones_server import DroneServer
from src.environment.pygame_handler import PygameHandler
from src.utils.Consts import Paths
from src.utils.util_classes import ThreeDVector


class Main:
    def __init__(self):
        self.drones_server = DroneServer()
        self.mission_control = MissionControl()
        self.pygame_handler = PygameHandler(self.drones_server.clients)


def main():
    pg = Main()
    missions = pickle.load(open(Paths.ENVIRONMENT_PATHS, 'rb'))
    for i in range(20):
        m = missions[i]
        d = DroneAgent(name=f"drone_{i}", initial_position=ThreeDVector(threeDtuple=m[0], y_x_z=True),
                       target=ThreeDVector(threeDtuple=m[1], y_x_z=True))
        d.drone.mission_controller.set_mission(
            Mission(ThreeDVector(threeDtuple=m[0], y_x_z=True), ThreeDVector(threeDtuple=m[1],y_x_z=True), path=m[2]))
        d.drone.mission_controller.mission_start()
    pg.drones = pg.pygame_handler.start_simulation()


if __name__ == "__main__":
    main()