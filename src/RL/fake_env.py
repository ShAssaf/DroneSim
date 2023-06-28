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
                                ((RadarSpec.RANGE, RadarSpec.RANGE), (RadarSpec.RANGE, RadarSpec.RANGE)))

    def get_env(self, pos: ThreeDVector):
        return self.map.image[int(pos.y):int(pos.y + RadarSpec.RANGE * 2),
               int(pos.x): int(pos.x + RadarSpec.RANGE * 2)]

    def get_close_env(self, pos: ThreeDVector):
        return self.map.image[
               int(pos.y + RadarSpec.RANGE - Consts.CLOSE_RANGE):int(pos.y + RadarSpec.RANGE + Consts.CLOSE_RANGE),
               int(pos.x + RadarSpec.RANGE - Consts.CLOSE_RANGE): int(pos.x + RadarSpec.RANGE + Consts.CLOSE_RANGE)]

    def get_reward(self, pos: ThreeDVector, target: ThreeDVector, velocity: ThreeDVector):
        """get reward for current position and done flag"""
        # todo: add battary level
        if pos.x < 0 - RadarSpec.RANGE or pos.y < 0 - RadarSpec.RANGE or pos.x > self.map.image.shape[0] or pos.y > \
                self.map.image.shape[1]:
            return -(pos - target).get_magnitude(), False
        # done on exits screen
        # if pos.x < 0 or pos.y < 0 or pos.x > self.map.image.shape[0]-RadarSpec.RANGE*2 or pos.y >
        # self.map.image.shape[1]-RadarSpec.RANGE*2:
        #     return -100000, True
        elif not np.all(self.get_close_env(pos) == 0):
            print("drone hit obstacle")
            sleep(0.2)
            return -100000, True
        if (pos - target).get_magnitude() < Consts.DISTANCE_TO_TARGET:
            if velocity.get_magnitude() < 1:
                (10 - velocity.get_magnitude()) * 100, True
            return (10 - velocity.get_magnitude()) * 1000000, False
        else:
            return -(pos - target).get_magnitude(), False

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
