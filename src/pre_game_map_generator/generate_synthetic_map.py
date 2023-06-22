import cv2
import numpy as np


def create_array_with_circles(size, num_circles, max_circle_radius, inner_radius):
    # Create an empty array
    array = np.zeros((size, size))

    # Create indices for the x and y coordinates
    y, x = np.ogrid[-size/2:size/2, -size/2:size/2]
    distance_to_center = np.sqrt(x**2 + y**2)

    # Mask for the inner circle
    mask_inner_circle = distance_to_center < inner_radius

    for _ in range(num_circles):
        # Randomly pick a center point for the circle
        center_x, center_y = np.random.randint(-size/2 + max_circle_radius, size/2 - max_circle_radius, size=2)

        # Randomly pick a radius and value for the circle
        circle_radius = np.random.randint(1, max_circle_radius)
        circle_value = np.random.randint(150, 250)

        # Calculate the distance from every point in the array to the center of the circle
        distance_to_circle_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)

        # Create a mask for the points within the circle
        mask_circle = distance_to_circle_center < circle_radius

        # Only update the array where the mask for the circle is True and the mask for the inner circle is False
        array[np.logical_and(mask_circle, np.logical_not(mask_inner_circle))] = circle_value

    return array

# Create the array
size = 1000
num_circles = 80
max_circle_radius = 35
inner_radius = 100
arr = create_array_with_circles(size, num_circles, max_circle_radius, inner_radius)
cv2.imwrite("data/circles.png", arr)