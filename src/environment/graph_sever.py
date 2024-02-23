import pickle
from os.path import exists

import cv2
#cv2.CV_IO_MAX_IMAGE_PIXELS = 2 ** 128
# cv2.CV_IO_MAX_IMAGE_WIDTH = 1000000
# cv2.CV_IO_MAX_IMAGE_HEIGHT = 1000000
# cv2.CV_IO_MAX_IMAGE_PIXELS = 17179869184
import networkx as nx
from flask import Flask, request, jsonify

from src.utils.Consts import Consts, Paths
from src.utils.shortest_path_3d import create_graph

app = Flask(__name__)
env_graph = None


def load_graph():  # this takes ~ 2min on Shlomo's machine when the graph exists
    print("Loading graph...")
    if not exists(Paths.ENVIRONMENT_GRAPH):
        print("Graph does not exist. Creating graph...")
        create_graph(cv2.imread(Paths.RESCALED_MAP_PATH, cv2.IMREAD_GRAYSCALE), scale_down=10)
        # tomer add fix this path
    with open(Paths.ENVIRONMENT_GRAPH, "rb") as file:
        global env_graph
        env_graph = pickle.load(file)
        print("Graph loaded successfully.")


@app.route('/graph', methods=['POST'])
def calculate():
    try:
        # Assuming the client sends a JSON request with data to calculate
        request_data = request.json
        print("Received request data: ", request_data)
        # Perform your calculation here
        result = perform_calculation(request_data)
        print("Calculation result: ", result)
        return jsonify({"result": result})
    except Exception as e:
        print("Error occurred: ", str(e))
        return jsonify({"error": str(e)}), 400


def perform_calculation(data):
    global env_graph
    print("Performing calculation with data: ", data)
    print("Start: ", data['start'], " Target: ", data['target'])
    result = nx.shortest_path(env_graph, tuple(data['start']), tuple(data['target']), weight='weight')
    print("Calculation completed. Result: ", result)
    return result


# push context manually to app
with app.app_context():
    load_graph()

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True, port=Consts.GRAPH_PORT)
