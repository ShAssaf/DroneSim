import math
import pickle
import random
from itertools import product

import cv2
import networkx as nx

from src.utils.Consts import Paths, Consts


def shortest_path_3d_environment(grid, start, end):
    # Create a graph from the 2D grid
    graph = create_graph(grid)

    # save graph object to file
    pickle.dump(graph, open('filename.pickle', 'wb'))
    path = nx.shortest_path(graph, start, end, weight='weight')

    return path


def create_graph(grid, scale_down=10):
    graph = nx.Graph()
    rows, cols = len(grid), len(grid[0])
    combs = list(product(list(map(lambda x: x * scale_down, [-1, 0, 1])), repeat=3))  # all combinations of 3d vectors

    # Helper function to check if a cell is within bounds and meets height constraints
    def is_valid(x, y, h):
        return 0 <= x < rows and 0 <= y < cols and h - grid[x][y] >= 0

    def vertical_validity(i, j, h, new_x, new_y, new_z):
        if (i != new_x or j != new_y) and h < Consts.VERTICAL_TAKE_OFF_MIN:
            return False
        return True

    for i in range(0, rows, scale_down):
        for j in range(0, cols, scale_down):
            for h in range(0, 401, scale_down):
                for dx, dy, dz in combs:
                    new_x, new_y, new_z = i + dx, j + dy, h + dz
                    if is_valid(new_x, new_y, new_z) and is_valid(i, j, h) and vertical_validity(i, j, h, new_x, new_y,
                                                                                                 new_z):
                        graph.add_node((i, j, h))
                        # Add an edge to the neighbor with a cost of 1
                        graph.add_edge((i, j, h), (new_x, new_y, new_z), weight=math.sqrt(dx ** 2 + dy ** 2 + dz ** 2))
        # if i % 1000 == 0:
        #     pickle.dump(graph, open(f'{i}.pickle', 'wb'))
    pickle.dump(graph, open(Paths.ENVIRONMENT_GRAPH, 'wb'))

    return graph


def generate_paths():
    # Load the graph object from file
    paths = []
    graph = pickle.load(open(Paths.ENVIRONMENT_GRAPH, 'rb'))
    image = cv2.imread("/Users/shlomoassaf/reps/DroneSim/data/part_new_york_3kmm.jpg", cv2.IMREAD_GRAYSCALE)
    height_zero_points = [(x, y) for x in range(0, len(image), 10) for y in range(0, len(image[0]), 10) if
                          image[x][y] == 0]
    c = 0
    while True:
        if c > 1000:
            break
        c += 1
        points = random.choices(height_zero_points, k=2)

        # if distance > 300 then add to result
        if math.sqrt((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2) > 300:
            path = nx.shortest_path(graph, (points[0][0], points[0][1], 0), (points[1][0], points[1][1], 0),
                                    weight='weight')
            if len(path) > 0:
                paths.append(((points[0][0], points[0][1], 0), (points[1][0], points[1][1], 0), path))
                print(path)
                print(len(paths))

            pickle.dump(paths, open(Paths.ENVIRONMENT_PATHS, 'wb'))
            print("Saved")