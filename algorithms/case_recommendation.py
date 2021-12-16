from typing import Dict
from math import sqrt, log
from graph import CitationNetwork
from algorithms.random_walker import RandomWalker
from helpers import top_n

MAX_NUM_STEPS = 200000
MAX_WALK_LENGTH = 5

VISITED_FREQ_THRESHOLD = 100
NUM_VISITED_THRESHOLD = 25


class CaseRecommendation:
    citation_network: CitationNetwork
    random_walker: RandomWalker

    def __init__(self, citation_network: CitationNetwork):
        self.citation_network = citation_network
        self.random_walker = RandomWalker(self.citation_network)

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
        average_case_year = self.average_year_of_cases(opinion_ids)
        for key, value in overall_node_freq_dict.items():
            curr_node_metadata = self.citation_network.network_edge_list.node_metadata[key]
            year_diff = abs(average_case_year - curr_node_metadata.year) if curr_node_metadata.year is not None else 0
            # overall_node_freq_dict[key] = self.relevance_adjusted_score(value, num_neighbors=curr_node_metadata.length)
        top_n_recommendations = top_n(overall_node_freq_dict, num_recommendations)
        print(top_n_recommendations)
        return top_n_recommendations

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
        while num_steps < max_num_steps:  # Keep a constant worst-case bound on execution time
            random_walk_dest, walk_length = self.random_walker.random_walk(opinion_id, max_walk_length=5)
            if random_walk_dest == opinion_id:
                continue
            if random_walk_dest not in node_freq_dict:
                node_freq_dict[random_walk_dest] = 0
            node_freq_dict[random_walk_dest] += 1
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
            node_metadata = self.citation_network.network_edge_list.node_metadata[op_id]
            node_degrees[op_id] = node_metadata.length
            total_num_edges += node_metadata.length
            if node_metadata.length > max_degree:
                max_degree = node_metadata.length
        if total_num_edges == 0:
            return {op_id: 0 for op_id in opinion_ids}
        denormalized_weights = {op_id: self.denormalized_case_weight(node_degree, max_degree, total_num_edges)
                                for op_id, node_degree in node_degrees.items()}
        denormalized_weight_sum = sum(denormalized_weights.values())
        normalized_weights = {op_id: node_weight / denormalized_weight_sum for op_id, node_weight in
                              denormalized_weights.items()}
        return normalized_weights

    def denormalized_case_weight(self, node_degree, max_degree, total_num_edges):
        return (node_degree * (max_degree - log(node_degree))) / total_num_edges

    def time_adjusted_score(self, unadjusted_score, year_distance) -> float:
        pass

    def obscurity_adjusted_score(self, unadjusted_score, num_neighbors) -> float:
        pass

    def relevance_adjusted_score(self, unadjusted_score, num_neighbors) -> float:
        floored_num_neighbors = min(max(num_neighbors, 50), 1000)
        return unadjusted_score / log(floored_num_neighbors)

    def landmark_adjusted_score(self, unadjusted_score, num_neighbors) -> float:
        floored_num_neighbors = min(max(num_neighbors, 50), 1000)
        return unadjusted_score * log(floored_num_neighbors)

    def average_year_of_cases(self, nodes: frozenset) -> float:
        sum_years, num_nodes = 0, 0
        for node in nodes:
            if (node_year := self.citation_network.network_edge_list.node_metadata[node].year) is not None:
                sum_years += node_year
                num_nodes += 1
        return sum_years / num_nodes
