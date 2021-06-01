from functools import cache
from typing import Dict

import networkx as nx
import numpy as np

RANDOM_WALK_NUM_STEPS = 3


class RandomWalker:
    """
    Future potential optimization: load all edges into a single array as described in Section 3.3 of
    Eksombatchai et al. (2018) and use offsets to randomly access. Current method is very slow and
    dynamically allocates neighbor dicts (bad bad bad)
    """
    network: nx.Graph

    def __init__(self, network):
        self.network = network

    def random_walk(self, source_node, num_steps=RANDOM_WALK_NUM_STEPS, weighted=True) -> str:
        """
        Performs a random walk from the specified source node for the specified number of steps.

        :param source_node: The source node's identifier (opinion resource_id)
        :param num_steps: The number of steps to randomly walk from the node
        :param weighted: Whether to weight the random walk with citation depth
        :return: The destination node's identifier
        """
        curr_node = source_node
        for step in range(num_steps):
            curr_node = self.random_neighbor(curr_node, weighted=weighted)
        return curr_node

    def random_neighbor(self, source_node, weighted=True) -> str:
        destination_weight_dict = self.get_edge_weight_dict(source_node)
        destination_nodes = list(destination_weight_dict.keys())
        prob_distribution = list(destination_weight_dict.values()) if weighted is True else [1 for _ in range(len(destination_nodes))]
        np_prob_dist = np.array(prob_distribution, dtype='float')
        np_prob_dist /= np_prob_dist.sum()
        random_selection = np.random.choice(destination_nodes, 1, p=np_prob_dist)
        return random_selection[0]

    @cache
    def get_edge_weight_dict(self, source_node) -> Dict[str, int]:
        return {node: metadata['weight'] for node, metadata in self.network[source_node].items()}
