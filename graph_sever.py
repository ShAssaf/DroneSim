import pickle
from os.path import exists

import cv2
import networkx as nx
from flask import Flask, request, jsonify

from src.utils.Consts import Consts, Paths
from src.utils.shortest_path_3d import create_graph

app = Flask(__name__)
env_graph = None


def load_graph():  # this takes ~ 2min on Shlomo's machine
    if not exists(Paths.ENVIRONMENT_GRAPH):
        create_graph(cv2.imread(Paths.MAP_PATH, cv2.IMREAD_GRAYSCALE), scale_down=10)
    with open(Paths.ENVIRONMENT_GRAPH, "rb") as file:
        global env_graph
        env_graph = pickle.load(file)


@app.route('/graph', methods=['POST'])
def calculate():
    try:
        # Assuming the client sends a JSON request with data to calculate
        request_data = request.json
        # Perform your calculation here
        result = perform_calculation(request_data)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def perform_calculation(data):
    global env_graph
    return nx.shortest_path(env_graph, tuple(data['start']), tuple(data['target']))


# push context manually to app
with app.app_context():
    load_graph()

if __name__ == '__main__':
    app.run(debug=True, port=Consts.GRAPH_PORT)
