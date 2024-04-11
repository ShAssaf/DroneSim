import pickle

from src.drone.drone_agent import DroneAgent
from src.drone.misson_control import MissionControl
from src.environment.drones_server import DroneServer
from src.environment.pygame_handler import PygameHandler
from src.utils.util_classes import ThreeDVector


class Main:
    def __init__(self):
        self.drones_server = DroneServer()
        self.mission_control = MissionControl()
        self.pygame_handler = PygameHandler(self.drones_server.clients)


def main():
    pg = Main()
    drones = []
    for i in range(10):
        random_mission = MissionControl.load_valid_mission()
        d = DroneAgent(name=f"drone_{i}", initial_position=ThreeDVector(threeDtuple=random_mission.start_point))
        d.drone.mission_control.set_mission(random_mission)
        drones.append(d)
    for d in drones:
        d.drone.mission_control.mission_start()
    pg.pygame_handler.start_simulation()  # todo move it to init


if __name__ == "__main__":
    main()
