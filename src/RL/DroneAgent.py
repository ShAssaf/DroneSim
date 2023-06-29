import math
import pickle
import socket
import threading

import numpy as np
import pandas as pd
import torch

from src.RL.dqn import DQNAgent
from src.RL.fake_env import FakeEnv
from src.drone.Drone import SmallDrone
from src.utils.Consts import Consts, RadarSpec
from src.utils.util_classes import InternalGPS, ThreeDVector, debug_print

X = 0
Y = 1


class DroneAgent:
    """this is reinforcement learning agent that will be used to control the drone"""

    def __init__(self, name: str, target: ThreeDVector = ThreeDVector(200, 200, 0),
                 initial_position: ThreeDVector = ThreeDVector(500, 500, 0)):
        self.drone = SmallDrone(name, InternalGPS(initial_position))
        self._socket_to_server = None
        self.env = FakeEnv()
        self.target = target
        self.source_target_df = pd.read_csv(Consts.DRONE_POSITIONS_PATH)
        self.initial_position = initial_position
        self.connect_to_server()
        self.out_of_map = False

    def get_state(self):
        # todo: add battary level
        radar_data = self.drone.radar.get_sensor_data(compact=True, as_vector=True)
        velocity_angle = self.drone.get_velocity().get_angle()
        velocity_magnitude = self.drone.get_velocity().get_magnitude()
        target_vector = self.target - self.drone.get_gps()
        target_angle = target_vector.get_angle()
        target_magnitude = target_vector.get_magnitude()
        relative_angle = target_angle - velocity_angle
        battery_level = 100  # self.drone.power_controller.get_battery_level()
        return np.concatenate((radar_data, [velocity_magnitude, target_magnitude, relative_angle, battery_level]))

    def step(self, action):
        if action == 0:
            self.drone.motion_controller.accelerate(1, 0, 0)
        elif action == 1:
            self.drone.motion_controller.accelerate(-1, 0, 0)
        elif action == 2:
            self.drone.motion_controller.accelerate(0, 1, 0)
        elif action == 3:
            self.drone.motion_controller.accelerate(0, -1, 0)
        elif action == 4:
            pass
        self.drone.gps.calculate_position()
        try:
            self.drone.radar.update_sense_circle(self.env.get_env(self.drone.get_gps()),
                                                 self.drone.gps.get_velocity().get_angle())
        except:
            self.drone.radar.update_sense_circle(np.ones((2 * RadarSpec.RANGE, 2 * RadarSpec.RANGE)),
                                                 self.drone.gps.get_velocity().get_angle())
            self.out_of_map = True

    def learn(self):

        # Initialize environment and the agent
        state_size = 22  # 6 REGIONS * 3 SCOPES + VELOCITY_MAGNITUDE + TARGET_RANGE + RELATIVE ANGLE + BATTERY_LEVEL
        action_size = 5  # acceleration in x, -x , y, -y, or do nothing direction currently ignore z direction
        agent = DQNAgent(state_size, action_size)

        # Set parameters
        episodes = 1000  # number of games we want the agent to play
        batch_size = 32

        # Iterate over episodes
        e = 0
        while True:
            self.out_of_map = False
            e+=1
            # reset drone position and drone target
            source, target = self.env.get_source_target()
            self.drone.set_gps(source[X], source[Y], 0)
            self.drone.gps.set_speed(0, 0, 0)
            self.target = ThreeDVector(target[X], target[Y], 0)
            state = self.get_state()
            rewards = []

            # Time steps within each episode
            for s in range(500000):
                # Agent takes action
                action = agent.select_action(state)
                self.step(action)
                if self.out_of_map:
                    break
                reward, done = self.env.get_reward(self.drone.get_gps(), self.target, self.drone.gps.get_velocity())
                next_state = self.get_state()
                rewards.append(reward)
                # Remember the experience
                agent.store_experience(state, action, reward, next_state)

                # make next_state the new current state.
                state = next_state

                if s > 150:
                    agent.modify_learning_rate()

                # Training
                # Perform training if there are enough experiences in the replay memory
                if len(agent.replay_buffer.buffer) >= batch_size:
                    agent.train(batch_size)
                # If episode ends (e.g., if the drone has arrived at the target or crashed)
                if done:
                    break
            print(f"episode: {e}, step: {s}, reward {sum(rewards)}")

            # Save weights every 50 episodes
            if e % 50 == 0:
                agent.save("dqn_weights.h5")

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
                        a = self.drone.get_gps()
                        # Serialize the object
                        serialized_data = pickle.dumps(a)
                        # Send the serialized object
                        self._socket_to_server.sendall(serialized_data)
                    elif command == "get_velocity":
                        # Serialize the object
                        serialized_data = pickle.dumps(self.drone.gps.get_velocity())
                        # Send the serialized object
                        self._socket_to_server.sendall(serialized_data)
                    elif command == "get_battery_status":
                        serialized_data = pickle.dumps(self.drone.power_controller.get_battery_percentage())
                        self._socket_to_server.sendall(serialized_data)
                    elif command == "get_drone_name":
                        serialized_data = pickle.dumps(self.drone.name)
                        self._socket_to_server.sendall(serialized_data)
                    elif command.startswith("accelerate"):
                        accelerate_vec = [float(i) for i in command.split(":")[1].split(",")]
                        self.drone.motion_controller.accelerate(accelerate_vec[0], accelerate_vec[1],
                                                                accelerate_vec[2])
                    elif command == "update":
                        self.drone.calculate_gps()
                        self.drone.power_controller.calculate_battery(self.drone.get_velocity())
                    elif command == "start_learning":
                        t = threading.Thread(target=self.learn, args=())
                        t.start()
                    elif command == "get_target_vector":
                        serialized_data = pickle.dumps(self.target - self.drone.get_gps())
                        self._socket_to_server.sendall(serialized_data)
                    elif command != "":
                        print("Unknown command: " + command)


