from time import sleep

import numpy as np
import pandas as pd

from src.utils.Consts import RadarSpec, Consts
from src.utils.map_obj import MapObject
from src.utils.util_classes import ThreeDVector


class FakeEnv:
    PAD = RadarSpec.RANGE

    def __init__(self, ):
        self.map = MapObject()
        # pad the map image with zeros for RadarSpec.RANGE
        self.map.image = np.pad(self.map.image,
                                ((RadarSpec.RANGE, RadarSpec.RANGE), (RadarSpec.RANGE, RadarSpec.RANGE)),
                                mode='constant', constant_values=255)

    def get_env(self, pos: ThreeDVector):
        return self.map.image[int(pos.y):int(pos.y + RadarSpec.RANGE * 2),
               int(pos.x): int(pos.x + RadarSpec.RANGE * 2)]

    def get_close_env(self, pos: ThreeDVector):
        return self.map.image[
               int(pos.y + RadarSpec.RANGE - Consts.CLOSE_RANGE):int(pos.y + RadarSpec.RANGE + Consts.CLOSE_RANGE),
               int(pos.x + RadarSpec.RANGE - Consts.CLOSE_RANGE): int(pos.x + RadarSpec.RANGE + Consts.CLOSE_RANGE)]

    def get_reward(self, pos: ThreeDVector, target: ThreeDVector, velocity: ThreeDVector, battery_level: float):
        """get reward for current position and done flag"""
        # todo: add battery level
        velocity_angle = velocity.get_angle()
        velocity_magnitude = velocity.get_magnitude()
        target_vector = target - pos
        target_angle = target_vector.get_angle()
        target_magnitude = target_vector.get_magnitude()
        relative_angle = target_angle - velocity_angle

        if not np.all(self.get_close_env(pos) == 0):
            print("drone hit obstacle")
            return -10000000, True
        if target_magnitude < Consts.DISTANCE_TO_TARGET:
            if velocity_magnitude < 1:
                return 10000000000, True
            return (10 - velocity_magnitude) * 1000, False
        else:
            if velocity_magnitude < 1:
                return -1000000, False
            return (90-abs(relative_angle)*100)*velocity_magnitude, False

    @staticmethod
    def get_source_target() -> ((int, int), (int, int)):
        """get random source,target for csv file"""

        csv_file = pd.read_csv(Consts.DRONE_POSITIONS_PATH)
        source_target = csv_file.sample(1)
        source = list(source_target['source'])
        source = [int(i) for i in source[0].replace('(', '').replace(')', '').split(',')]
        target = list(source_target['target'])
        target = [int(i) for i in target[0].replace('(', '').replace(')', '').split(',')]
        return source, target
