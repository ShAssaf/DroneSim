import numpy as np
import pandas as pd


def calculate_distance_matrix(x, y):
    """Calculate the angle between the x axis and the point (x,y)"""

    # Calculate the center coordinates of the image
    center_x = x // 2
    center_y = y // 2

    # Create a meshgrid of x and y coordinates
    x_coords = np.arange(x)
    y_coords = np.arange(y)
    x_mesh, y_mesh = np.meshgrid(x_coords, y_coords)

    # Calculate the distances from the center
    distances = np.sqrt((x_mesh - center_x) ** 2 + (y_mesh - center_y) ** 2)
    pd.DataFrame(distances).to_csv("data/radar_pre_calculated_data/distances.csv")
    return distances


def calculate_angle_matrix(x, y):
    """Calculate the angle between the x axis and the point (x,y) example of 3*3 output:
    array([[ -45.,    0.,   45.],
           [ -90.,    0.,   90.],
           [-135.,  180.,  135.]])
    """

    # Calculate the center coordinates of the image
    center_x = x // 2
    center_y = y // 2

    # Create a meshgrid of x and y coordinates
    x_coords = np.arange(x)
    y_coords = np.arange(y)
    x_mesh, y_mesh = np.meshgrid(x_coords, y_coords)
    y_mesh = np.flip(np.flip(y_mesh, axis=0), axis=1)

    # Calculate the angle from the center
    angles = np.degrees(np.arctan2((y_mesh - center_y), (x_mesh - center_x)))
    angles = np.flip(np.rot90(angles), axis=1).astype(int)
    pd.DataFrame(angles).to_csv("data/radar_pre_calculated_data/angles.csv")
    return angles
