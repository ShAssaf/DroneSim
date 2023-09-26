import pickle
import socket
import threading
from time import sleep

import numpy as np

from src.RL.doubleQ import QLearning
from src.RL.fake_env import FakeEnv
from src.drone.Drone import SmallDrone
from src.utils.Consts import RadarSpec, Consts
from src.utils.util_classes import ThreeDVector, InternalGPS


class DroneAgent:
    def __init__(self, name: str, target: ThreeDVector = ThreeDVector(200, 200, 0),
                 initial_position: ThreeDVector = ThreeDVector(500, 500, 0)):
        self.drone = SmallDrone(name, InternalGPS(initial_position))
        self._socket_to_server = None
        self.env = FakeEnv()
        self.target = self.drone.mission_controller.mission.target
        self.QAgent = QLearning()
        self.out_of_map = False

        self.initial_position = initial_position
        self.connect_to_server()

    def get_state(self):
        # todo: add battary level
        radar_data = self.drone.radar.get_sensor_data(compact=True, as_vector=True)
        velocity_angle = self.drone.get_velocity().get_angle()
        velocity_magnitude = self.drone.get_velocity().get_magnitude()
        target_vector = self.target - self.drone.get_location()
        target_angle = target_vector.get_angle()
        target_magnitude = target_vector.get_magnitude()
        relative_angle = target_angle - velocity_angle
        battery_level = 100  # self.drone.power_controller.get_battery_level()
        return np.concatenate(
            (radar_data,
             [relative_angle / 180, velocity_magnitude / 10],
             [target_angle / 180, target_magnitude / 1000],
             [battery_level / 100]))  # normalize

    def step(self, action):
        if action == 0:
            self.drone.motion_controller.accelerate2(0)
        elif action == 1:
            self.drone.motion_controller.accelerate2(1)
        elif action == 2:
            self.drone.motion_controller.turn_to(0)
        elif action == 3:
            self.drone.motion_controller.turn_to(1)
        elif action == 4:
            pass
        self.drone.gps.calculate_position()
        try:
            self.drone.radar.update_sense_circle(self.env.get_env(self.drone.gps.get_gps()),
                                                 self.drone.gps.get_velocity().get_angle())
        except:
            self.drone.radar.update_sense_circle(np.ones((2 * RadarSpec.RANGE, 2 * RadarSpec.RANGE)),
                                                 self.drone.gps.get_velocity().get_angle())
            self.out_of_map = True

    def start(self):

        sum_reward = []
        e_reward = 0
        episodes = 4000000

        ### for Loop that train the model num_episodes times by playing the game
        for e in range(episodes):
            source, target = (np.random.randint(200, 700), np.random.randint(100, 400)), (
                np.random.randint(200, 700), np.random.randint(100, 400))
            self.drone.set_gps(source[0], source[1], 0)
            self.out_of_map = False
            self.drone.gps.set_speed(0, 0, 0)
            self.target = ThreeDVector(target[0], target[1], 0)
            state = self.get_state()
            e_reward = 0
            # Play the game!
            while True:

                # 4. Run agent on the state
                action = self.QAgent.choose_action(state)
                self.step(action)

                # 5. Agent performs action
                next_state = self.get_state()
                reward, done = self.env.get_reward(self.drone.get_gps(), self.target, self.drone.gps.get_velocity(),
                                                   self.drone.power_controller.get_battery_percentage())


                # 7. Learn
                self.QAgent.update(state, action, reward, next_state)



                # 9. Update state
                state = next_state

                e_reward += reward
                # 10. Check if end of game
                if done or self.out_of_map:
                    break

            if e % 100 == 0:
                self.QAgent.vector_ds.clean()
                self.QAgent.vector_ds.save()
            sum_reward.append(e_reward/1000)



    def connect_to_server(self):
        self._socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_to_server.connect((Consts.HOST, Consts.PORT))
        thread = threading.Thread(target=self.communicate_with_server, args=())

        # Start the thread
        thread.start()

    def communicate_with_server(self):

        while True:
            # delay to not overload the agent
            # sleep(0.1)
            data = self._socket_to_server.recv(1024).decode().split(';')

            if not data:
                "print no data"
            else:
                for command in data:
                    if command == "get_location":
                        serialized_data = pickle.dumps(self.drone.get_location())
                        self._socket_to_server.sendall(serialized_data)
                    elif command == "get_velocity":
                        serialized_data = pickle.dumps(self.drone.gps.get_velocity())
                        self._socket_to_server.sendall(serialized_data)
                    elif command == "get_battery_status":
                        serialized_data = pickle.dumps(self.drone.power_controller.get_battery_percentage())
                        self._socket_to_server.sendall(serialized_data)
                    elif command == "get_drone_name":
                        serialized_data = pickle.dumps(self.drone.name)
                        self._socket_to_server.sendall(serialized_data)
                    elif command.startswith("accelerate2"):
                        self.drone.motion_controller.accelerate2(float(command.split(":")[1]))
                    elif command.startswith("turn_to"):
                        self.drone.motion_controller.turn_to(float(command.split(":")[1]))
                    elif command.startswith("accelerate"):
                        accelerate_vec = [float(i) for i in command.split(":")[1].split(",")]
                        self.drone.motion_controller.accelerate(accelerate_vec[0], accelerate_vec[1], accelerate_vec[2])
                    elif command == "update":
                        self.drone.calculate_gps()
                        self.drone.power_controller.calculate_battery(self.drone.get_velocity())
                    # elif command == "start_learning":
                    #     t = threading.Thread(target=self.start, args=())
                    #     t.start()
                    elif command == "get_target_vector":
                        serialized_data = pickle.dumps(self.target - self.drone.get_location())
                        self._socket_to_server.sendall(serialized_data)
                    elif command != "":
                        print("Unknown command: " + command)

