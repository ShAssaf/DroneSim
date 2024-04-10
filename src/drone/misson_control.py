import random
from enum import Enum

import cv2
import requests

from src.utils.Consts import Consts, MapConsts
from src.utils.logger import get_logger
from src.utils.util_classes import ThreeDVector

logger = get_logger(__name__)


class STATUS(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    SUSPENDED = 4


class Mission:

    def __init__(self, start_point, target=ThreeDVector(-1, -1, -1), mission_type='Dummy', path=None):
        self.start_point = start_point
        self.target = target
        self.mission_type = mission_type
        self.mission_status = STATUS.PENDING
        self.mission_id = None
        if path is None:
            self.path = Path(Path.get_path_from_server(start_point, target))
        else:
            self.path = Path(path)

    def set_path(self, path):
        self.path = Path(path)

    def __str__(self):
        return f"Mission: {self.mission_type} from {str(self.start_point)} to {str(self.target)}"


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
            result = response.json()["result"]
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

    def generate_mission(self, start, target):
        return Mission(start, target)

    @staticmethod
    def generate_random_mission():
        map = cv2.imread(MapConsts.MAP_PATH, cv2.IMREAD_GRAYSCALE)
        mapy, mapx = map.shape
        while True:
            start = ThreeDVector(random.randint(0, mapx)//10 * 10, random.randint(0, mapy)//10 * 10, 0)
            target = ThreeDVector(random.randint(0, mapx)//10 * 10, random.randint(0, mapy)//10 * 10, 0)
            if map[start.y, start.x] == 0 and map[target.y, target.x] == 0:
                m = Mission(start, target)
                if m.path.points is not None:
                    return m


class VehicleMissionControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.mission = Mission(self.vehicle.get_location(), path=['dummy'])

    def set_mission(self, mission):
        logger.info(f"{self.vehicle.name}: Mission set to {str(mission)}")
        self.mission = mission

    def mission_start(self):
        self.mission.mission_status = STATUS.IN_PROGRESS

    def mission_step(self):
        np = self.mission.path.get_next_point()
        if self.vehicle.gps.distance(np) < 10:
            logger.info(f"{self.vehicle.name}: Arrived at point {np}")
            self.mission.path.set_next_point()
            if self.mission.path.get_next_point() is None:
                logger.info(f"{self.vehicle.name}: Arrived at target {self.mission.target}")
                self.mission.mission_status = STATUS.COMPLETED
                self.vehicle.motion_controller.stop()
                return
        self.vehicle.motion_controller.go_to_point(self.mission.path.get_next_point())
