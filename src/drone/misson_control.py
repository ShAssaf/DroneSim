import pickle
from enum import Enum
from os.path import exists

import cv2
import networkx as nx

from src.utils.Consts import Paths
from src.utils.shortest_path_3d import create_graph
from src.utils.util_classes import debug_print, ThreeDVector


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
        self.path = None

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
        return self.points[self.current_point]


class MissionControl:
    def __init__(self, mission_queue=[]):
        self.mission_queue = mission_queue
        self.env_graph = None
        self.mission_status = None
        self.drones = None
        self.inactive_drones = None
        pass
        # self.gogogo()

    def load_graph(self):
        if not exists(Paths.ENVIRONMENT_GRAPH):
            create_graph(cv2.imread(Paths.MAP_PATH, cv2.IMREAD_GRAYSCALE), scale_down=10)
        with open(Paths.ENVIRONMENT_GRAPH, "rb") as file:
            self.env_graph = pickle.load(file)

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
        while True:
            if self.mission.mission_status == STATUS.IN_PROGRESS:
                self.mission_step()
            elif self.mission.mission_status == STATUS.COMPLETED:
                break
            else:
                debug_print("Mission failed")

    def mission_step(self):
        if self.vehicle.gps.distance(self.mission.path.get_next_point()) < 10:
            self.mission.path.set_next_point()
        next_point = self.mission.path.get_next_point()
        if next_point is None:
            self.mission.mission_status = STATUS.COMPLETED
        self.vehicle.motion_controller.go_to_point(self.mission.path.get_next_point())
