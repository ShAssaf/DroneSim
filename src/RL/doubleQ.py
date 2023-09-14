import os
import pickle
import random

import numpy as np
from scipy.spatial import KDTree

STATE_SIZE = 23
ACTION_SIZE = 5
K = 5


class ReplayBuffer:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.buffer = []

    def add_experience(self, experience):
        if len(self.buffer) >= self.max_capacity:
            self.buffer.pop(0)
        self.buffer.append(experience)

    def sample_batch(self, batch_size):
        return random.sample(self.buffer, batch_size)


class QLearning:
    def __init__(self, actions=ACTION_SIZE, alpha=0.5, gamma=0.95, epsilon=0.1):
        self.actions = [i for i in range(actions)]
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.vector_ds = VectorsKD()
        self.replay_buffer = ReplayBuffer(1000)

    def choose_action(self, state):
        # EXPLORE
        if np.random.uniform(0, 1) < self.epsilon:
            action = np.random.choice(self.actions)
        # EXPLOIT
        else:
            neighbors_average = np.array(self.vector_ds.get_neighbors_average_value(state))
            action = np.random.choice(np.flatnonzero(neighbors_average == neighbors_average.max())) # random tie breaking

            # decrease exploration_rate
        self.epsilon *= self.epsilon
        self.epsilon = max(0.01, self.epsilon)
        return action

    def update(self, state, action, reward, next_state):
        predict = self.vector_ds.get_neighbors_average_value(state)[action]
        target = reward + self.gamma * max(self.vector_ds.get_neighbors_average_value(next_state))
        self.vector_ds.update_q(state, action, self.alpha * (target - predict))


class VectorsKD:
    def __init__(self):
        self.load()
        self.distance_threshold = 1
        self.max_neighbor = 10
        self.max_capacity = 10 ** 6
        self.kd_tree = KDTree(np.array([np.array(k) for k in self.Q.keys()]))
        self.kd_data = self.kd_tree.data
        self.vectors_to_remove = []
        self.new_vectors = []

    def query(self, state):
        neighbor_dist, neighbors_idx = self.kd_tree.query(state, distance_upper_bound=self.distance_threshold)
        if not isinstance(neighbors_idx, list):
            neighbors_idx = [neighbors_idx]
        if not isinstance(neighbor_dist, list):
            neighbor_dist = [neighbor_dist]
        n_list = [neighbors_idx[idx] for idx in range(len(neighbors_idx)) if
                  neighbor_dist[idx] < self.distance_threshold]
        if len(n_list) >self.max_neighbor:
            self.Q[state] = self.get_neighbors_average_value(state)
            self.vectors_to_remove.extend([self.kd_data[idx]] for idx in n_list)
        return n_list

    def clean(self):
        """ during debug need to make sure the amount of points in each cluster is not too
         big and that the amount of clusters is not too small

         also consider changing threshold
         """
        # cluster all vectors and then take the average of each cluster and replace the cluster with the average
        # this will reduce the size of the dictionary
        # points = self.kd_tree.data
        # if points:
        #     # Use DBSCAN to find high-density regions, treating points in low-density regions as "noise"
        #     eps = self.distance_threshold  # maximum distance between two points in the same neighborhood
        #     min_samples = 1  # minimum number of points to form a dense region
        #     dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        #     labels = dbscan.fit_predict(points)
        #     new_points = self.new_vectors
        #     # Group the original points by their labels
        #     clusters = {}
        #     for i, label in enumerate(labels):
        #         if label not in clusters:
        #             clusters[label] = []
        #         clusters[label].append(points[i])
        #     for cluster, points in clusters:
        #         q_values = [self.Q[point] for point in points]
        #         q_avg = [sum(x) / len(x) for x in zip(*q_values)]
        #         new_points[random.choice(points)] = q_avg
        #data_copy = self.kd_data.copy()
        for v in self.vectors_to_remove:
            self.Q.pop(v)
        self.vectors_to_remove = []

        self.kd_tree = KDTree(np.array([np.array(k) for k in self.Q.keys()]))
        self.kd_data = self.kd_tree.data
        self.new_vectors = []

    def get_neighbors_average_value(self, state):
        neighbors = self.query(state)
        if neighbors:
            q_neighbors = [self.Q[tuple(self.kd_data[neighbor])] for neighbor in neighbors]
            q_avg = [sum(x) / len(x) for x in zip(*q_neighbors)]
        else:
            self.new_vectors.append(state)
            self.Q[tuple(state)] = [1000] * ACTION_SIZE
            q_avg = [1000] * ACTION_SIZE
        return q_avg

    def update_q(self, state, action, new_q_values):
        neighbors = self.query(state)
        for neighbor in neighbors:
            self.Q[tuple(self.kd_data[neighbor])][action] += new_q_values
        if tuple(state) not in self.Q:
            self.Q[tuple(state)] = [1000] * ACTION_SIZE
        self.Q[tuple(state)][action] += new_q_values


    def load(self):
        if os.path.isfile('saved_dictionary.pkl'):
            with open('saved_dictionary.pkl', 'rb') as f:
                self.Q = pickle.load(f)
        else:
            self.Q = {tuple([0] * STATE_SIZE): [0] * ACTION_SIZE}

    def save(self):
        pickle.dump(self.Q, open("saved_dictionary.pkl", "wb"))
