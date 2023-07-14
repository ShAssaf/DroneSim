import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


# Define the replay memory buffer
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


# Define the Q-network
class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        q_values = self.fc3(x)
        return q_values


# Define the DQN agent
class DQNAgent:
    def __init__(self, state_size, action_size, learning_rate=0.01, discount_factor=0.95, epsilon=0.9):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # Initialize replay memory
        self.replay_buffer = ReplayBuffer(max_capacity=10000)

        # Build Q-network
        self.q_network = QNetwork(state_size, action_size)
        self.load("dqn_weights.h5")
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)

    def store_experience(self, state, action, reward, next_state):
        experience = (state, action, reward, next_state)
        self.replay_buffer.add_experience(experience)

    def select_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.from_numpy(state).float().unsqueeze(0)
        q_values = self.q_network(state)
        return torch.argmax(q_values).item()

    def train(self, batch_size):
        batch = self.replay_buffer.sample_batch(batch_size)
        states, actions, rewards, next_states = zip(*batch)

        states = torch.from_numpy(np.vstack(states)).float()
        actions = torch.from_numpy(np.vstack(actions)).long()
        rewards = torch.from_numpy(np.vstack(rewards)).float()
        next_states = torch.from_numpy(np.vstack(next_states)).float()

        q_values = self.q_network(states)
        q_values = q_values.gather(1, actions)

        next_q_values = self.q_network(next_states)
        max_next_q_values = torch.max(next_q_values, dim=1, keepdim=True)[0]

        targets = rewards + self.discount_factor * max_next_q_values
        loss = nn.MSELoss()(q_values, targets)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def modify_learning_rate(self):
        if self.learning_rate > 0.001:
            self.learning_rate *= 0.999
            self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)

    def load(self, name):
        try:
            self.q_network.load_state_dict(torch.load(name))
        except FileNotFoundError:
            print("No weights found")

    def save(self, name):
        torch.save(self.q_network.state_dict(), name)
