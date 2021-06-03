from functools import cache
from typing import Dict
import networkx as nx
import numpy as np
from random import randrange
from graph.network_edge_list import NetworkEdgeList


class RandomWalker:
    """
    Future potential optimization: load all edges into a single array as described in Section 3.3 of
    Eksombatchai et al. (2018) and use offsets to randomly access. Current method is very slow and
    dynamically allocates neighbor dicts (bad bad bad)
    """
    network: nx.Graph
    network_edge_list: NetworkEdgeList

    def __init__(self, network):
        self.network = network
        self.network_edge_list = NetworkEdgeList()

    def random_walk(self, source_node, max_walk_length) -> (str, int):
        """
        Performs a random walk from the specified source node for the specified number of steps.

        :param source_node: The source node's identifier (opinion resource_id)
        :param max_walk_length: The number of steps to randomly walk from the node
        :return: The destination node's identifier
        """
        walk_length = randrange(0, max_walk_length) + 1
        curr_node = source_node
        for step in range(walk_length):
            curr_node = self.random_neighbor_fast(curr_node)
        return curr_node, walk_length

    def random_neighbor_fast(self, source_node):
        node_info = self.network_edge_list.node_metadata[source_node]
        return self.network_edge_list.edge_list[randrange(node_info['start'], node_info['end'])]

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
