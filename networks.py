import os
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

class CriticNetwork(nn.Module):
    def __init__(self, beta, input_dims, fc1_dims, fc2_dims, 
                    n_agents, n_actions, name, chkpt_dir):
        super(CriticNetwork, self).__init__()

        self.chkpt_file = os.path.join(chkpt_dir, name)
        os.makedirs(os.path.dirname(self.chkpt_file), exist_ok=True)

        self.fc1 = nn.Linear(input_dims+n_agents*n_actions, fc1_dims)
        self.fc2 = nn.Linear(fc1_dims, fc2_dims)
        self.q = nn.Linear(fc2_dims, 1)

        self.optimizer = optim.Adam(self.parameters(), lr=beta)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, obstacle, self_, other, dirty, action):
        state1 = T.stack([obstacle, self_, other, dirty], dim=1)
        x = F.relu(self.conv1(state1))
        x = F.relu(self.conv2(x))
        x = x.flatten(start_dim=1)
        
        state2 = action.flatten(start_dim=1)
        x = F.relu(self.fc1(T.cat([x, state2], dim=1)))
        x = F.relu(self.fc2(x))
        q = self.q(x)

        return q

    def save_checkpoint(self):
        T.save(self.state_dict(), self.chkpt_file)

    def load_checkpoint(self):
        self.load_state_dict(T.load(self.chkpt_file))


class ActorNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims, 
                 n_actions, name, chkpt_dir):
        super(ActorNetwork, self).__init__()

        self.chkpt_file = os.path.join(chkpt_dir, name)
        os.makedirs(os.path.dirname(self.chkpt_file), exist_ok=True)

        self.fc1 = nn.Linear(input_dims, fc1_dims)
        self.fc2 = nn.Linear(fc1_dims, fc2_dims)
        self.pi = nn.Linear(fc2_dims, n_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=alpha)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, obstacle, self_, other, dirty):
        state1 = T.stack([obstacle, self_, other, dirty], dim=1)
        x = F.relu(self.conv1(state1))
        x = F.relu(self.conv2(x))
        x = x.flatten(start_dim=1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        pi = T.softmax(self.pi(x), dim=1)

        return pi

    def save_checkpoint(self):
        T.save(self.state_dict(), self.chkpt_file)

    def load_checkpoint(self):
        self.load_state_dict(T.load(self.chkpt_file))

