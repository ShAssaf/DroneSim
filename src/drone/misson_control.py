from enum import Enum

import networkx as nx
import requests

from src.utils.Consts import Consts
from src.utils.util_classes import ThreeDVector


class STATUS(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3


class Mission:

    def __init__(self, start_point, target=ThreeDVector(-1, -1, -1), mission_type='Dummy'):
        self.start_point = start_point
        self.target = target
        self.mission_type = mission_type
        self.mission_status = STATUS.PENDING
        self.mission_id = None
        self.path = Path(Path.get_path_from_server(start_point, target))

    def set_path(self, path):
        self.path = Path(path)


class Path:
    def __init__(self, points):
        self.points = points
        self.current_point = 0


    def set_next_point(self):
        if self.current_point < len(self.points):
            self.current_point += 1

    def get_next_point(self):
        if self.current_point < len(self.points):
            return self.points[self.current_point]
        return None


    @staticmethod
    def get_path_from_server(start, target):
        data = {"start": (start[0], start[1], start[2]), "target": (target[0], target[1], target[2])}
        response = requests.post(f"http://127.0.0.1:{Consts.GRAPH_PORT}/graph", json=data)
        if response.status_code == 200:
            result = [(i[1], i[0], i[2]) for i in response.json()["result"]]  # need to inverse graph coordinates

            return result
        else:
            print("Error:", response.json()["error"])
            return None

class MissionControl:
    def __init__(self, mission_queue=[]):
        self.mission_queue = mission_queue
        self.env_graph = None
        self.mission_status = None
        self.drones = None
        self.inactive_drones = None
        pass
        # self.gogogo()


    def gogogo(self):
        while True:
            if len(self.mission_queue) > 0:
                current_mission = self.mission_queue.pop(0)
                drone = self.find_nearest_drone(current_mission)
                current_mission.set_path(nx.shortest_path(self.env_graph, drone.location, current_mission.target))
                drone.mission_controller.set_mission(current_mission)
                drone.mission_start()

    def find_nearest_drone(self, mission: Mission):
        if len(self.inactive_drones) == 0:
            Exception("No drones available")
        closet_drone = self.inactive_drones[0]
        dis = closet_drone.location.distance(mission.start_point)
        for drone in self.inactive_drones:
            cur_dis = drone.location.distance(mission.target)
            if cur_dis < dis:
                closet_drone = drone
                dis = cur_dis
        return closet_drone


class VehicleMissionControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.mission = Mission(self.vehicle.get_location())

    def set_mission(self, mission):
        self.mission = mission

    def mission_start(self):
        self.mission.mission_status = STATUS.IN_PROGRESS

    def mission_step(self):
        if self.vehicle.gps.distance(self.mission.path.get_next_point()) < 10:
            self.mission.path.set_next_point()
            if self.mission.path.get_next_point() is None:
                self.mission.mission_status = STATUS.COMPLETED
                return
        self.vehicle.motion_controller.go_to_point(self.mission.path.get_next_point())
