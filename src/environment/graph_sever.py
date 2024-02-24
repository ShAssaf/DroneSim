import cv2
import networkx as nx
from flask import Flask, request, jsonify

from src.utils.Consts import Consts
from src.utils.shortest_path_3d import create_graph, Neo4jClient

app = Flask(__name__)


def load_graph():  # this takes ~ 2min on Shlomo's machine when the graph exists
    print("Loading graph...")
    if not client.check_if_graph_exists():
        # todo : fix path
        create_graph(cv2.imread("data/maps/rescaled_map_1_pixel_per_1_meter_building_deionised.jpg",
                                cv2.IMREAD_GRAYSCALE), scale_down=10)


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
    print("Performing calculation with data: ", data)
    print("Start: ", data['start'], " Target: ", data['target'])
    result = client.get_path_between_nodes(data['start'][0], data['start'][1], data['start'][2])
    print("Calculation completed. Result: ", result)
    return result


# push context manually to app
with app.app_context():
    client = Neo4jClient()

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True, port=Consts.GRAPH_PORT)
