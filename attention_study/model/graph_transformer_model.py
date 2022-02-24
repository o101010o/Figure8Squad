# ai/ml imports
import torch.optim as optim
import torch.nn as nn
import torch
import numpy as np
import random

# graph transformer imports
from graph_transformer.main_molecules_graph_regression import main
from graph_transformer.nets.molecules_graph_regression.load_net import gnn_model 

# our code
from attention_study.model.utils import get_cost_from_reward

MAXIMUM_THEORETICAL_REWARD = 25

def initialize_train_artifacts():
    params, net_params = main(return_config=True, config_file='model/graph_transformer_config.json')
    device = net_params['device']

    # setting seeds
    random.seed(params['seed'])
    np.random.seed(params['seed'])
    torch.manual_seed(params['seed'])
    if device.type == 'cuda':
        torch.cuda.manual_seed(params['seed'])

    model = gnn_model('GraphTransformer', net_params)
    model = model.to(device)

    optimizer = optim.Adam(model.parameters(), lr=params['init_lr'], weight_decay=params['weight_decay'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min',
                                                     factor=params['lr_reduce_factor'],
                                                     patience=params['lr_schedule_patience'],
                                                     verbose=True)
    
    
    return model, optimizer, scheduler


def optimize(optimizer, baseline, reward, ll, TEST_SETTINGS, num_steps=1, attention_input=None):
    local_max_theoretical_reward = MAXIMUM_THEORETICAL_REWARD
    if TEST_SETTINGS['normalize_losses_rewards_by_ep_length']:
        reward /= num_steps
        ll /= num_steps
        local_max_theoretical_reward /= num_steps
    # set costs
    model_cost = get_cost_from_reward(reward)
    #bl_val = get_cost_from_reward(local_max_theoretical_reward)
    #bl_loss = 0
    #reinforce_loss = ((bl_val - model_cost) * ll).mean()
    #loss = reinforce_loss + bl_loss
    net_loss = nn.L1Loss()()
    optimizer.zero_grad()
    loss = model_cost
    loss.backward()
    optimizer.step()
    return None, loss
