import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import MultivariateNormal
from torch.distributions import Normal

import sys


import numpy as np 


class CustomValueNetwork(nn.Module):
	"""
	Approximation of the value function V of a state given as input
	FC network with 1 hidden layer and ReLU activations
	Class used as 'critic'
	Inputs :
	input_size : dimension of each state
	hidden_size : number of hidden layers
	output_size : 1 (dimension of the value function estimate)
	"""

	def __init__(self, input_size, hidden_size, output_size=1):
		super(CustomValueNetwork, self).__init__()
		self.fc1 = nn.Linear(input_size, hidden_size)
		self.fc2 = nn.Linear(hidden_size, hidden_size)
		self.fc3 = nn.Linear(hidden_size, output_size)

	def forward(self, x):
		out = F.relu(self.fc1(x.float()))
		out = F.relu(self.fc2(out))
		out = self.fc3(out)
		return out

	def predict(self, x):
		return self(x).cpu().detach().numpy()[0]


class CustomDiscreteActorNetwork(nn.Module):
	"""
	Custom policy model network for discrete action space
	Inputs :
	input_size : state space dimension
	hidden_size : nb of hidden layers (64 in author's paper for continous action space)
	action_size : action space dimension
	"""
	def __init__(self, input_size, hidden_size, action_size):
		super(CustomDiscreteActorNetwork, self).__init__()
		self.fc1 = nn.Linear(input_size, hidden_size)
		self.fc2 = nn.Linear(hidden_size, hidden_size)
		self.fc3 = nn.Linear(hidden_size, action_size)

	def forward(self, x):
		out = torch.tanh(self.fc1(x))
		out = torch.tanh(self.fc2(out))
		out = torch.tanh(self.fc2(out))
		out = F.softmax(self.fc3(out), dim=-1)
		return out

	def select_action(self, x):
		return torch.multinomial(self(x), 1).cpu().detach().numpy()


class ContinuousActorNetwork(nn.Module):
	"""
	Policy model network for continuous action space (from the paper)
	Inputs :
	input_size : state space dimension
	hidden_size : nb of hidden layers used by the authors
	action_size : action space dimension
	"""
	def __init__(self, input_size, hidden_size, action_size, std, env):
		super(ContinuousActorNetwork, self).__init__()
		self.fc1 = nn.Linear(input_size, hidden_size)
		self.fc2 = nn.Linear(hidden_size, hidden_size)
		self.fc3 = nn.Linear(hidden_size, action_size)
		self.std = std
		self.env = env

	def forward(self, x):
		raise NotImplementedError

	def evaluate(self,x):

		out = torch.tanh(self.fc1(x.float()))
		out = torch.tanh(self.fc2(out))
		out = torch.tanh(self.fc2(out))
		out = torch.tanh(self.fc3(out))

		if np.isnan(out.cpu().detach().numpy()).any():
			#print(batch_observations)
			print("Nan")
			sys.exit(0)
		return out

	def select_action(self, x):
		action_mean = self.evaluate(x)

		if np.isnan(action_mean.cpu().detach().numpy()).any():
			#print(batch_observations)
			print("Naaaaaaaaan")

		#cov_mat = torch.eye(action_mean.size()[1])*self.std
		#dist = MultivariateNormal(action_mean, cov_mat)

		dist = Normal(action_mean, scale = torch.tensor(self.std*np.ones(action_mean.size()[1])).float())
		action = dist.sample()

		if np.isnan(action.cpu().detach().numpy()).any():
			print("NAAAAAAAAAAAAAN")
		#action_logprob = dist.log_prob(action)
		#sampled_a = max(self.env.action_space.low, sampled_a)
		#sampled_a = min(self.env.action_space.high, sampled_a)
	 
		return action.detach()

