import math
import pickle
from itertools import product

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


