import numpy as np
from flask import Flask, request, jsonify

from src.utils.Consts import RadarSpec, Consts
from src.utils.map_obj import MapObject
from src.utils.util_classes import ThreeDVector

app = Flask(__name__)


class FakeEnv:
    PAD = RadarSpec.RANGE

    def __init__(self):
        self.map = MapObject()
        self.map.image = np.pad(self.map.image,
                                ((RadarSpec.RANGE, RadarSpec.RANGE), (RadarSpec.RANGE, RadarSpec.RANGE)),
                                mode='constant', constant_values=255)
        self.drones_locations = []

    def get_env(self, pos: ThreeDVector):
        return self.map.image[int(pos.y):int(pos.y + RadarSpec.RANGE * 2),
               int(pos.x): int(pos.x + RadarSpec.RANGE * 2)]

    def get_close_env(self, pos: ThreeDVector):
        return self.map.image[
               int(pos.y + RadarSpec.RANGE - Consts.CLOSE_RANGE):int(pos.y + RadarSpec.RANGE + Consts.CLOSE_RANGE),
               int(pos.x + RadarSpec.RANGE - Consts.CLOSE_RANGE): int(pos.x + RadarSpec.RANGE + Consts.CLOSE_RANGE)]

    def get_reward(self, pos: ThreeDVector, target: ThreeDVector, velocity: ThreeDVector, battery_level: float):
        velocity_angle = velocity.get_angle()
        velocity_magnitude = velocity.get_magnitude()
        target_vector = target - pos
        target_angle = target_vector.get_angle()
        target_magnitude = target_vector.get_magnitude()
        relative_angle = target_angle - velocity_angle

        if not np.all(self.get_close_env(pos) == 0):
            print("drone hit obstacle")
            return -10000000, True
        if target_magnitude < Consts.DISTANCE_TO_TARGET:
            if velocity_magnitude < 1:
                return 10000000000, True
            return (10 - velocity_magnitude) * 1000, False
        else:
            if velocity_magnitude < 1:
                return -1000000, False
            return (90 - abs(relative_angle) * 100) * velocity_magnitude, False

    # @staticmethod
    # def get_source_target() -> ((int, int), (int, int)):
    #     csv_file = pd.read_csv(Consts.DRONE_POSITIONS_PATH)
    #     source_target = csv_file.sample(1)
    #     source = list(source_target['source'])
    #     source = [int(i) for i in source[0].replace('(', '').replace(')', '').split(',')]
    #     target = list(source_target['target'])
    #     target = [int(i) for i in target[0].replace('(', '').replace(')', '').split(',')]
    #     return source, target


env = FakeEnv()


@app.route('/get_env', methods=['POST'])
def get_env():
    data = request.get_json()
    pos = ThreeDVector(data['pos']['x'], data['pos']['y'], data['pos']['z'])
    env_data = env.get_env(pos)
    return jsonify({'env_data': env_data.tolist()})


@app.route('/get_close_env', methods=['POST'])
def get_close_env():
    data = request.get_json()
    pos = ThreeDVector(data['pos']['x'], data['pos']['y'], data['pos']['z'])
    close_env_data = env.get_close_env(pos)
    return jsonify({'close_env_data': close_env_data.tolist()})


@app.route('/get_reward', methods=['POST'])
def calculate_reward():
    data = request.get_json()
    pos = ThreeDVector(data['pos']['x'], data['pos']['y'], data['pos']['z'])
    target = ThreeDVector(data['target']['x'], data['target']['y'], data['target']['z'])
    velocity = ThreeDVector(data['velocity']['x'], data['velocity']['y'], data['velocity']['z'])
    battery_level = data['battery_level']
    reward, done = env.get_reward(pos, target, velocity, battery_level)
    return jsonify({'reward': reward, 'done': done})


# @app.route('/get_source_target', methods=['GET'])
# def get_source_target():
#     source, target = env.get_source_target()
#     return jsonify({'source': source, 'target': target})


if __name__ == '__main__':
    app.run(debug=True, port=Consts.ENV_PORT)
