import csv
import math
from itertools import product

from neo4j import GraphDatabase
from tqdm import tqdm

from src.utils.Consts import Consts, Paths


def create_graph(grid, scale_down=10):
    rows, cols = len(grid), len(grid[0])
    combs = list(product(list(map(lambda x: x * scale_down, [-1, 0, 1])), repeat=3))

    def is_valid(x, y, h):
        return 0 <= x < rows and 0 <= y < cols and h - grid[x][y] >= 0

    def vertical_validity(i, j, h, new_x, new_y):
        if (i != new_x or j != new_y) and h < Consts.VERTICAL_TAKE_OFF_MIN:
            return False
        return True

    nodes = [(i, j, h) for i in range(0, rows, scale_down) for j in range(0, cols, scale_down) for h in
             range(0, 401, scale_down)]

    nodes_ids = {(i, j, h): idx for idx, (i, j, h) in enumerate(nodes)}

    relations = []
    # with driver.session() as session:
    for i in tqdm(range(0, rows, scale_down)):
        for j in range(0, cols, scale_down):
            for h in range(0, 401, scale_down):
                for dx, dy, dz in combs:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    new_x, new_y, new_z = i + dx, j + dy, h + dz
                    if is_valid(new_x, new_y, new_z) and is_valid(i, j, h) and vertical_validity(i, j, h, new_x,
                                                                                                 new_y, new_z):
                        if (new_x, new_y, new_z) not in nodes_ids:
                            # print(f"Node {new_x, new_y, new_z} not in nodes_ids")
                            continue
                        relations.append((
                            nodes_ids.get((i, j, h)),
                            nodes_ids.get((new_x, new_y, new_z)),
                            math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
                        ))
    # Write nodes to CSV
    with open('nodes.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id:ID', 'x', 'y', 'z'])
        for idx, node in enumerate(nodes):
            writer.writerow([idx] + list(node))

    # Write relations to CSV
    with open('relations.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([':START_ID', ':END_ID', 'distance:FLOAT'])
        for rel in relations:
            writer.writerow(rel)

    # save to neo4j
    import subprocess

    # Define the command as a list of strings
    command = [
        "neo4j-admin",
        "database",
        "import",
        "full",
        f"--nodes={Paths.BASE_PATH}/nodes.csv",
        f"--relationships={Paths.BASE_PATH}/relations.csv",
        "--delimiter=,",
        "--overwrite-destination",
        "--verbose"
    ]

    # Execute the command
    try:
        subprocess.run(command, check=True)
        print("Import process completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Import process failed with error code {e.returncode}.")
        print(e.output)


class Neo4jClient:
    def __init__(self):
        self._uri = "bolt://localhost:7687"
        self._user = "neo4j"
        self._password = "11559900"
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def close(self):
        self._driver.close()

    def check_if_graph_exists(self):
        print("Checking if graph exists...")
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                RETURN n
                LIMIT 1
                """
            )
            print("Graph exists") if result.single() else print("Graph does not exist")
            return True if result else False

    def get_path_between_nodes(self, p1, p2):
        "return list of all the points in the path between p1 and p2"
        with self._driver.session() as session:
            query = f"""
            MATCH p = shortestPath((startNode {{x: '{p1[0]}', y: '{p1[1]}', z: '{p1[2]}'}})-[*]-(endNode {{x: '{p2[0]}', y: '{p2[1]}', z: '{p2[2]}'}}))
            RETURN p
            """
            result = session.run(query).single()[0]
            path = [node._properties for node in result.nodes]
            x_y_z_path = [(int(node['x']), int(node['y']), int(node['z'])) for node in path]

            return x_y_z_path
