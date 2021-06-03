from typing import Dict
import networkx as nx
from graph.random_walker import RandomWalker
from helpers import top_n

MAX_NUM_STEPS = 100000
MAX_WALK_LENGTH = 5

VISITED_FREQ_THRESHOLD = 100
NUM_VISITED_THRESHOLD = 25


class CaseRecommendation:
    network: nx.Graph
    random_walker: RandomWalker

    def __init__(self, network):
        self.network = network
        self.random_walker = RandomWalker(self.network)

    def recommendations_for_case(self, opinion_id, num_recommendations,
                                 max_walk_length=MAX_WALK_LENGTH, max_num_steps=MAX_NUM_STEPS) -> Dict[str, float]:
        """
        Random-walk recommendation algorithm to return relevant cases given a case ID. Heavily based on
        Eksombatchai et. al (2018)'s Pixie recommendation algorithm for Pinterest.

        :param opinion_id: The opinion ID to get recommendations for (source for the random walks)
        :param num_recommendations:
        :param max_walk_length: Maximum number of steps
        :param max_num_steps:
        :return:
        """
        node_freq_dict = {}
        num_steps = 0
        num_nodes_met_threshold = 0
        while num_steps < max_num_steps:  # Keep a constant worst-case bound on execution time
            random_walk_dest, walk_length = self.random_walker.random_walk(opinion_id, max_walk_length=max_walk_length)
            if random_walk_dest not in node_freq_dict:
                node_freq_dict[random_walk_dest] = 0
            node_freq_dict[random_walk_dest] += 1
            if node_freq_dict[random_walk_dest] == VISITED_FREQ_THRESHOLD:
                num_nodes_met_threshold += 1
                if num_nodes_met_threshold == NUM_VISITED_THRESHOLD:
                    break
            num_steps += walk_length
        return top_n(node_freq_dict, num_recommendations)
