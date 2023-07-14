import datetime
import os
import pickle
import random
import socket
import threading

import torch
import numpy as np
from pathlib import Path

from src.RL.neural import DroneNet
from collections import deque

from src.RL.fake_env import FakeEnv
from src.RL.metrics import MetricLogger
from src.drone.Drone import SmallDrone
from src.utils.Consts import RadarSpec, Consts
from src.utils.util_classes import ThreeDVector, InternalGPS


class DroneAgent2:
    def __init__(self, name: str, target: ThreeDVector = ThreeDVector(200, 200, 0),
                 initial_position: ThreeDVector = ThreeDVector(500, 500, 0)):
        self.drone = SmallDrone(name, InternalGPS(initial_position))
        self._socket_to_server = None
        self.env = FakeEnv()
        self.target = target
        self.initial_position = initial_position
        self.connect_to_server()
        self.out_of_map = False
        self.state_dim = 31
        self.action_dim = 5
        self.memory = deque(maxlen=100000)
        self.batch_size = 32

        self.exploration_rate = 1
        self.exploration_rate_decay = 0.999
        self.exploration_rate_min = 0.1
        self.gamma = 0.9

        self.curr_step = 0
        self.burnin = 1e3  # min. experiences before training
        self.learn_every = 3  # no. of experiences between updates to Q_online
        self.sync_every = 1e2  # no. of experiences between Q_target & Q_online sync

        self.save_every = 500  # no. of experiences between saving Mario Net
        self.save_dir = 'src/RL/checkpoints/'  # where to save Mario Net

        self.use_cuda = torch.cuda.is_available()

        self.net = DroneNet(self.state_dim, self.action_dim).float()
        if self.use_cuda:
            self.net = self.net.to(device='cuda')
        self.load()

        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=0.00025)
        self.loss_fn = torch.nn.SmoothL1Loss()

    def act(self, state):
        """
        Given a state, choose an epsilon-greedy action and update value of step.

        Inputs:
        state(LazyFrame): A single observation of the current state, dimension is (state_dim)
        Outputs:
        action_idx (int): An integer representing which action Mario will perform
        """
        # EXPLORE
        if np.random.rand() < self.exploration_rate:
            action_idx = np.random.randint(self.action_dim)

        # EXPLOIT
        else:
            state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(state)
            state = state.unsqueeze(0)
            action_values = self.net(state, model='online')
            action_idx = torch.argmax(action_values, axis=1).item()

        # decrease exploration_rate
        self.exploration_rate *= self.exploration_rate_decay
        self.exploration_rate = max(self.exploration_rate_min, self.exploration_rate)

        # increment step
        self.curr_step += 1
        return action_idx

    def cache(self, state, next_state, action, reward, done):
        """
        Store the experience to self.memory (replay buffer)

        Inputs:
        state (LazyFrame),
        next_state (LazyFrame),
        action (int),
        reward (float),
        done(bool))
        """
        state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(state)
        next_state = torch.FloatTensor(next_state).cuda() if self.use_cuda else torch.FloatTensor(next_state)
        action = torch.LongTensor([action]).cuda() if self.use_cuda else torch.LongTensor([action])
        reward = torch.DoubleTensor([reward]).cuda() if self.use_cuda else torch.DoubleTensor([reward])
        done = torch.BoolTensor([done]).cuda() if self.use_cuda else torch.BoolTensor([done])

        self.memory.append((state, next_state, action, reward, done,))

    def recall(self):
        """
        Retrieve a batch of experiences from memory
        """
        batch = random.sample(self.memory, self.batch_size)
        state, next_state, action, reward, done = map(torch.stack, zip(*batch))
        return state, next_state, action.squeeze(), reward.squeeze(), done.squeeze()

    def td_estimate(self, state, action):
        current_Q = self.net(state, model='online')[np.arange(0, self.batch_size), action]  # Q_online(s,a)
        return current_Q

    @torch.no_grad()
    def td_target(self, reward, next_state, done):
        next_state_Q = self.net(next_state, model='online')
        best_action = torch.argmax(next_state_Q, axis=1)
        next_Q = self.net(next_state, model='target')[np.arange(0, self.batch_size), best_action]
        return (reward + (1 - done.float()) * self.gamma * next_Q).float()

    def update_Q_online(self, td_estimate, td_target):
        loss = self.loss_fn(td_estimate, td_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def sync_Q_target(self):
        self.net.target.load_state_dict(self.net.online.state_dict())

    def learn(self):
        if self.curr_step % self.sync_every == 0:
            self.sync_Q_target()

        if self.curr_step % self.save_every == 0:
            self.save()

        if self.curr_step < self.burnin:
            return None, None

        if self.curr_step % self.learn_every != 0:
            return None, None

        # Sample from memory
        state, next_state, action, reward, done = self.recall()

        # Get TD Estimate
        td_est = self.td_estimate(state, action)

        # Get TD Target
        td_tgt = self.td_target(reward, next_state, done)

        # Backpropagate loss through Q_online
        loss = self.update_Q_online(td_est, td_tgt)

        return td_est.mean().item(), loss

    def save(self):
        save_path = self.save_dir + f"/drone_net_{int(self.curr_step // self.save_every)}.chkpt"
        torch.save(
            dict(
                model=self.net.state_dict(),
                exploration_rate=self.exploration_rate
            ),
            save_path
        )
        print(f"DroneNet saved to {save_path} at step {self.curr_step}")

    def load(self, load_path='src/rl/checkpoints/'):
        try:
            if not os.path.exists(load_path):
                raise ValueError(f"{load_path} does not exist")
            checks = sorted([i for i in os.listdir(load_path) if i.endswith('.chkpt')])[-1]

            ckp = torch.load(load_path + checks, map_location=('cuda' if self.use_cuda else 'cpu'))
            for item in os.listdir(load_path):
                item_path = os.path.join(load_path, item)
                if os.path.isfile(item_path):
                    # Delete the file
                    os.remove(item_path)
            exploration_rate = ckp.get('exploration_rate')
            state_dict = ckp.get('model')

            print(f"Loading model at {load_path} with exploration rate {exploration_rate}")
            self.net.load_state_dict(state_dict)
            self.exploration_rate = exploration_rate
        except Exception as e:
            print(e)
            print("Loading failed. Creating new MarioNet")

    def get_state(self):
        # todo: add battary level
        radar_data = self.drone.radar.get_sensor_data(compact=True, as_vector=True)
        velocity_angle = self.drone.get_velocity().get_angle()
        velocity_magnitude = self.drone.get_velocity().get_magnitude()
        target_vector = self.target - self.drone.get_gps()
        target_angle = target_vector.get_angle()
        target_magnitude = target_vector.get_magnitude()
        # relative_angle = target_angle - velocity_angle
        battery_level = 100  # self.drone.power_controller.get_battery_level()
        return np.concatenate(
            (radar_data, [velocity_angle / 180, velocity_angle / 180, velocity_angle / 180,velocity_magnitude / 10,
                          velocity_magnitude / 10],
             [target_angle / 180, target_angle / 180, target_magnitude, target_magnitude, target_magnitude],
             [velocity_magnitude / 10, target_magnitude, battery_level / 100]))  # normalize

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
        save_dir = f"src/RL/checkpoints"
        logger = MetricLogger(save_dir)

        episodes = 4000000

        ### for Loop that train the model num_episodes times by playing the game
        for e in range(episodes):
            # if self.exploration_rate < 0.11:
            #     self.exploration_rate = 1
            source, target = (np.random.randint(200, 700), np.random.randint(100, 400)), (
                np.random.randint(200, 700), np.random.randint(100, 400))
            self.drone.set_gps(source[0], source[1], 0)
            self.out_of_map = False
            self.drone.gps.set_speed(0, 0, 0)
            self.target = ThreeDVector(target[0], target[1], 0)
            state = self.get_state()

            # Play the game!
            while True:

                # 4. Run agent on the state
                action = self.act(state)
                self.step(action)

                # 5. Agent performs action
                next_state = self.get_state()
                reward, done = self.env.get_reward(self.drone.get_gps(), self.target, self.drone.gps.get_velocity(),
                                                   self.drone.power_controller.get_battery_percentage())
                # 6. Remember
                self.cache(state, next_state, action, reward, done)

                # 7. Learn
                q, loss = self.learn()

                # 8. Logging
                logger.log_step(reward, loss, q)

                # 9. Update state
                state = next_state

                # 10. Check if end of game
                if done or self.out_of_map:
                    break

            logger.log_episode()

            if e % 20 == 0:
                logger.record(
                    episode=e,
                    epsilon=self.exploration_rate,
                    step=self.curr_step
                )

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
                        serialized_data = pickle.dumps(self.drone.get_gps())
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
                    elif command == "start_learning":
                        t = threading.Thread(target=self.start, args=())
                        t.start()
                    elif command == "get_target_vector":
                        serialized_data = pickle.dumps(self.target - self.drone.get_gps())
                        self._socket_to_server.sendall(serialized_data)
                    elif command.startswith("set_imitate"):
                        self.immitate_value = int(command.split(":")[1])
                        self.immitate_flag = True
                    elif command != "":
                        print("Unknown command: " + command)


