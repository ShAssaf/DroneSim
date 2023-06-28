import random

import numpy as np
import cv2
import networkx as nx
import pandas as pd
from scipy.spatial import distance
import math


class State:
    def __init__(self, state, is_terminal=False):
        self.state = state
        self.is_terminal = is_terminal

    def __str__(self):
        return f"state: {self.state}, is_terminal: {self.is_terminal}"

    def __repr__(self):
        return self.__str__()

def find_shortest_path(image, start, end):
    # Load the image

    # Threshold the image to create binary image (non-zero = obstacles)
    _, binary_image = cv2.threshold(image, 1, 1, cv2.THRESH_BINARY)

    # Invert the binary image to identify free space (non-obstacle)
    free_space = 1 - binary_image

    # Create a graph from the free space in the image
    graph = nx.grid_2d_graph(*free_space.shape)

    # Set weights for non-diagonal movements
    for u, v in graph.edges():
        graph[u][v]['weight'] = 1

    # Add edges for diagonal movement
    for node in graph.nodes:
        x, y = node
        if x + 1 < free_space.shape[0] and y + 1 < free_space.shape[1] and free_space[x + 1][y + 1]:
            graph.add_edge((x, y), (x + 1, y + 1), weight=math.sqrt(2))
        if x + 1 < free_space.shape[0] and y - 1 >= 0 and free_space[x + 1][y - 1]:
            graph.add_edge((x, y), (x + 1, y - 1), weight=math.sqrt(2))

    obstacle_indices = np.transpose(np.nonzero(binary_image))

    for index in map(tuple, obstacle_indices):
        graph.remove_node(index)
    try:
        # Compute the shortest path
        shortest_path = nx.dijkstra_path(graph, start, end, weight='weight')
    except :
        print("No path found")
        shortest_path = []
    return shortest_path


def draw_path(image_path, path):
    # Load the original image in color
    image_color = cv2.imread(image_path)

    # Draw the path on the image
    for point in path:
        cv2.circle(image_color, tuple(reversed(point)), 1, (0, 255, 0), -1)

    # Save the image with path
    cv2.imwrite('image_with_path.jpg', image_color)

    # If you want to see the image immediately
    cv2.imshow('Image with Path', image_color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_valid_source_target_position(map_image):
    """valid target position is a position that is reachable from source position, meaning there is pass of at least
    20 pixels width (with value 0) path between them all the way from source to target in the map image"""
    while True:
        source = [random.randint(0, map_image.shape[0] - 1), random.randint(0, map_image.shape[1] - 1)]
        target = [random.randint(0, map_image.shape[0] - 1), random.randint(0, map_image.shape[1] - 1)]
        if distance.euclidean(source, target) > 200 and len(find_shortest_path(map_image, source, target)) > 0:
            return source, target

def create_source_target_df(img_path):
    """create a df with source and target positions for each image"""
    s_t_dict= {'source': [], 'target': []}
    image = cv2.imread(img_path, 0)

    while len(s_t_dict['source']) < 1000:
        source, target = get_valid_source_target_position(image)
        s_t_dict['source'].append(source)
        s_t_dict['target'].append(target)
        df = pd.DataFrame(s_t_dict)
        df.to_csv(f"data/source_target.csv", index=False)

# image_path = "data/circles.png"
# create_source_target_df(image_path)
# Load your image (0: grayscale)
# image_path = "data/circles.png"
# image = cv2.imread(image_path, 0)
# # Threshold the image:
# _, binary_image = cv2.threshold(image, 1, 1, cv2.THRESH_BINARY)
#
# # Perform erosion to ensure path will be 20 pixels wide
# kernel = np.ones((20,20), np.uint8)
# eroded_image = cv2.erode(binary_image, kernel)
#
# # Create graph from eroded image
# G = nx.grid_2d_graph(*eroded_image.shape)
# for i in range(eroded_image.shape[0]):
#     for j in range(eroded_image.shape[1]):
#         if eroded_image[i, j] == 1:
#             G.remove_node((i, j))
#
# # Now find path between two points using A* algorithm
# start = (500, 500)
# end = (80, 300)
# path = nx.astar_path(G, start, end, heuristic=distance.euclidean)
# draw_path(image_path, path)
