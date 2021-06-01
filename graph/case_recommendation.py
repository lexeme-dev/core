from typing import Dict
import networkx as nx
import numpy as np

from graph.random_walker import RandomWalker

NUM_RANDOM_WALKS = 500


class CaseRecommendation:
    network: nx.Graph

    def __init__(self, network):
        self.network = network

    def recommendations_for_case(self, opinion_id, num_recommendations=10, num_walks=NUM_RANDOM_WALKS) -> Dict[str, float]:
        random_walker = RandomWalker(self.network)
        node_freq_dict = {}
        for i in range(num_walks):
            random_walk_dest = random_walker.random_walk(opinion_id)
            if random_walk_dest not in node_freq_dict:
                node_freq_dict[random_walk_dest] = 0
            node_freq_dict[random_walk_dest] += 1
        return {node: freq for node, freq in
                sorted(node_freq_dict.items(),
                       key=lambda kv_pair: kv_pair[1],
                       reverse=True)[:num_recommendations]
                }
