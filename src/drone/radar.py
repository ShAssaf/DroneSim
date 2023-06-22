import cv2
import numpy as np
import pandas as pd
from scipy.ndimage import rotate

from data.radar_pre_calculated_data.generate_radar_raw_data import calculate_angle_matrix, calculate_distance_matrix


# the radar use 1 pixel = 1 meter scale

class TwoDRadar:
    """Radar class for drone, the radar is a circular sensor that can detect objects in a certain radius R around the drone.
        it's get a map of the area and maintain a circle ."""

    REGIONS = [('FORWARD', (-10, 10)), ('FORWARD_RIGHT', (10, 45)), ('FORWARD_LEFT', (-45, -10)), ('RIGHT', (45, 160)),
               ('LEFT', (-160, -45)), ('BACKWARD', (160, -160))]
    SCOPES = [('Close', (0, 20)), ('Medium', (20, 100)), ('Far', (100, 500))]

    def __init__(self, r=5):
        self.distances = None
        self.angles = None
        self.indices_dict = {}
        self.sensor_date_dict = {}
        self.sensor_compact_date_dict = {}
        self.R = r

        self._last_angle = -1

        self.pre_calculation()

    def calculate_relative_angles(self, direction_angle: int):
        """Calculate the rotation matrix for the drone velocity direction and update the indices_dict"""
        if direction_angle == self._last_angle:
            return
        if direction_angle < 0:
            direction_angle = 360 + direction_angle
        angles = self.angles - direction_angle
        indices = np.where(angles < -180)
        angles[indices] += 360
        distances = self.distances
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
        self._last_angle = direction_angle

    def update_sense_circle(self, input_map: np.array, direction_angle: int):
        """Update the sense circle to the drone velocity direction"""
        if input_map.shape != (2 * self.R, 2 * self.R):
            raise ValueError("input map shape must be (2*R,2*R)")

        self.calculate_relative_angles(direction_angle)  # updates indices_dict with relative values
        for region in self.REGIONS:
            for scope in self.SCOPES:
                self.sensor_date_dict[(region[0], scope[0])] = input_map[self.indices_dict[(region[0], scope[0])]]
                self.sensor_compact_date_dict[(region[0], scope[0])] = np.log2(np.sum(
                    input_map[self.indices_dict[(region[0], scope[0])]] != 0) + 1).astype(int)

    def pre_calculation(self):
        """Calculate the distance and angle matrix indices for each region and range"""
        calculate_angle_matrix(2 * self.R, 2 * self.R)
        calculate_distance_matrix(2 * self.R, 2 * self.R)
        self.angles = pd.read_csv("data/radar_pre_calculated_data/angles.csv", index_col=0, header=None,
                                  skiprows=1).to_numpy()
        self.distances = pd.read_csv("data/radar_pre_calculated_data/distances.csv", index_col=0, header=None,
                                     skiprows=1).to_numpy()
        self.calculate_relative_angles(0)



# image = cv2.imread('/Users/shlomo/Documents/DroneSim/t.jpg', cv2.IMREAD_GRAYSCALE)
# a = TwoDRadar()
# a.update_sense_circle(image)


# def get_ramdom_image_part(image_path, shape):
#     """Get a random part of the image"""
#     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     x = np.random.randint(0, image.shape[0] - shape[0])
#     y = np.random.randint(0, image.shape[1] - shape[1])
#     return image[x:x + shape[0], y:y + shape[1]]


# test rotate function against calculate_angle_matrix conclusion - calc_rotate faster


# import time
# a = TwoDRadar()
# rotate_execution_time_list = []
# calc_execution_time_list = []
#
# for i in range(100):
#     img = get_ramdom_image_part('data/maps/no_bg/rescaled_map_1_pixel_per_1_meter_building_deionised.jpg', (1000, 1000))
#     angle = np.random.randint(-180, 180)
#     start_time = time.time()
#     rotate(img, angle)
#     end_time = time.time()
#     rotate_execution_time_list.append(end_time - start_time)
#     start_time = time.time()
#     a.calc_rotate(angle)
#     end_time = time.time()
#     calc_execution_time_list.append(end_time - start_time)
#     print('rotate mean time: ', np.mean(rotate_execution_time_list))
#     print('calc mean time: ', np.mean(calc_execution_time_list))
# pass
