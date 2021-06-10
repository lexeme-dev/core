from functools import cache
from typing import Dict
from math import sqrt, log
from graph.network_edge_list import NetworkEdgeList
from graph.random_walker import RandomWalker
from helpers import top_n

MAX_NUM_STEPS = 100000
MAX_WALK_LENGTH = 5

VISITED_FREQ_THRESHOLD = 100
NUM_VISITED_THRESHOLD = 25


class CaseRecommendation:
    network_edge_list: NetworkEdgeList
    random_walker: RandomWalker

    def __init__(self, network_edge_list: NetworkEdgeList):
        self.network_edge_list = network_edge_list
        self.random_walker = RandomWalker(self.network_edge_list)

    def recommendations(self, opinion_ids: frozenset, num_recommendations,
                        max_walk_length=MAX_WALK_LENGTH, max_num_steps=MAX_NUM_STEPS) -> Dict[str, float]:
        query_case_weights = self.input_case_weights(opinion_ids)
        overall_node_freq_dict = {}
        for opinion_id, weight in query_case_weights.items():
            curr_max_num_steps = int(weight * max_num_steps)
            curr_freq_dict = self.recommendations_for_case(int(opinion_id), num_recommendations=None,
                                                           max_walk_length=max_walk_length,
                                                           max_num_steps=curr_max_num_steps)
            for node, freq in curr_freq_dict.items():
                if node in opinion_ids:
                    continue
                if node not in overall_node_freq_dict:
                    overall_node_freq_dict[node] = 0
                overall_node_freq_dict[node] += sqrt(freq)  # See Eq. 3 of Eksombatchai et. al (2018)
        return top_n(overall_node_freq_dict, num_recommendations)

    def recommendations_for_case(self, opinion_id, num_recommendations,
                                 max_walk_length=MAX_WALK_LENGTH, max_num_steps=MAX_NUM_STEPS) -> Dict[str, float]:
        """
        Random-walk recommendation algorithm to return relevant cases given a case ID. Heavily based on
        Eksombatchai et. al (2018)'s Pixie recommendation algorithm for Pinterest.

        :param opinion_id: The opinion ID to get recommendations for (source for the random walks)
        :param num_recommendations: The number of cases to return
        :param max_walk_length: Maximum number of steps to perform in a single random walk
        :param max_num_steps: The upper bound of random-walk steps to execute while computing recommendations
        :return: A dictionary of the top num_recommendation opinion IDs and their visit values
        """
        node_freq_dict = {}
        num_steps = 0
        num_nodes_met_threshold = 0
        while num_steps < max_num_steps:  # Keep a constant worst-case bound on execution time
            random_walk_dest, walk_length = self.random_walker.random_walk(opinion_id, max_walk_length=max_walk_length)
            if random_walk_dest == opinion_id:
                continue
            if random_walk_dest not in node_freq_dict:
                node_freq_dict[random_walk_dest] = 0
            node_freq_dict[random_walk_dest] += 1
            # Early stopping based on visit thresholds; disabled pending further testing
            # if node_freq_dict[random_walk_dest] == VISITED_FREQ_THRESHOLD:
            #     num_nodes_met_threshold += 1
            #     if num_nodes_met_threshold == NUM_VISITED_THRESHOLD:
            #         break
            num_steps += walk_length
        return top_n(node_freq_dict, num_recommendations)

    def input_case_weights(self, opinion_ids) -> Dict[str, float]:
        """
        Given a set of opinion IDs in a query, give the probability distribution with which to visit them based on
        their degree centralities.

        :param opinion_ids: A set of opinion IDs
        :return: A dictionary with keys being the input case IDs and values being the relative weight to select them
        to begin the random walk.
        """
        total_num_edges, max_degree = 0, 0
        node_degrees = {}
        for op_id in opinion_ids:
            node_metadata = self.network_edge_list.node_metadata[op_id]
            node_degree = node_metadata['end'] - node_metadata['start']
            node_degrees[op_id] = node_degree
            total_num_edges += node_degree
            if node_degree > max_degree:
                max_degree = node_degree
        if total_num_edges == 0:
            return {op_id: 0 for op_id in opinion_ids}
        denormalized_weights = {op_id: self.denormalized_case_weight(node_degree, max_degree, total_num_edges)
                                for op_id, node_degree in node_degrees.items()}
        denormalized_weight_sum = sum(denormalized_weights.values())
        normalized_weights = {op_id: node_weight / denormalized_weight_sum for op_id, node_weight in denormalized_weights.items()}
        return normalized_weights

    def denormalized_case_weight(self, node_degree, max_degree, total_num_edges):
        return (node_degree * (max_degree - log(node_degree))) / total_num_edges
