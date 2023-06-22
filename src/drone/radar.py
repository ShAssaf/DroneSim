import cv2
import numpy as np
import pandas as pd
from scipy.ndimage import rotate

from data.radar_pre_calculated_data.generate_radar_raw_data import calculate_angle_matrix, calculate_distance_matrix


# the radar use 1 pixel = 1 meter scale

class TwoDRadar:
    DIRECTION = 0
    ANGLE_RANGE = 1
    """Radar class for drone, the radar is a circular sensor that can detect objects in a certain radius R around the drone.
        it's get a map of the area and maintain a circle ."""
    REGIONS = [('FORWARD', (-10, 10)), ('FORWARD_RIGHT', (10, 45)), ('FORWARD_LEFT', (-45, -10)), ('RIGHT', (45, 160)),
               ('LEFT', (-160, -45)), ('BACKWARD', (160, -160))]
    SCOPES = [('Close', (0, 20)), ('Medium', (20, 100)), ('Far', (100, 500))]

    def __init__(self, r=100):
        self.indices_dict = {}
        self.sensor_date_dict = {}
        self.sensor_compact_date_dict = {}
        self.R = r
        self.pre_calculation()

    def rotate_input_map_to_velocity_direction(self, input_map: np.array, direction_angle: float):
        """Rotate the input map to the drone velocity direction"""
        return rotate(input_map, angle=direction_angle)

    def update_sense_circle(self, input_map: np.array, direction_angle: float):
        """Update the sense circle to the drone velocity direction"""
        if input_map.shape != (2 * self.R, 2 * self.R):
            raise ValueError("input map shape must be (2*R,2*R)")
        input_map = self.rotate_input_map_to_velocity_direction(input_map, direction_angle)
        for region in self.REGIONS:
            for scope in self.SCOPES:
                self.sensor_date_dict[(region[0], scope[0])] = input_map[self.indices_dict[(region[0], scope[0])]]
                self.sensor_compact_date_dict[(region[0], scope[0])] = np.log2(np.sum(
                    input_map[self.indices_dict[(region[0], scope[0])]] != 0)+1).astype(int)

    def pre_calculation(self):
        """Calculate the distance and angle matrix indices for each region and range"""
        calculate_angle_matrix(2 * self.R, 2 * self.R)
        calculate_distance_matrix(2 * self.R, 2 * self.R)
        angles = pd.read_csv("data/radar_pre_calculated_data/angles.csv", index_col=0, header=None,
                             skiprows=1).to_numpy()
        distances = pd.read_csv("data/radar_pre_calculated_data/distances.csv", index_col=0, header=None,
                                skiprows=1).to_numpy()
        self.indices_dict = {}
        for region in self.REGIONS:
            for scope in self.SCOPES:
                if region[0] != 'BACKWARD':
                    self.indices_dict[(region[0], scope[0])] = np.where(
                        (angles >= region[1][0]) & (angles <= region[1][1]) &
                        (distances >= scope[1][0]) & (distances <= scope[1][1])
                    )
                else:
                    self.indices_dict[(region[0], scope[0])] = np.where(
                        ((angles >= region[1][0]) | (angles <= region[1][1])) &
                        (distances >= scope[1][0]) & (distances <= scope[1][1])
                    )



image = cv2.imread('/Users/shlomo/Documents/DroneSim/t.jpg', cv2.IMREAD_GRAYSCALE)

a = TwoDRadar()
pass
