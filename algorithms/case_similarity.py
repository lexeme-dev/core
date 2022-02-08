from functools import cache
import networkx as nx
import numpy as np
from typing import Set, Dict
from db.peewee.models import Similarity, Opinion, Cluster
from peewee import SQL, fn
from graph import CitationNetwork


class CaseSimilarity:
    citation_network: CitationNetwork

    def __init__(self, citation_network: CitationNetwork):
        self.citation_network = citation_network

    @staticmethod
    def jaccard_index(n1_neighbors: Set[str], n2_neighbors: Set[str]) -> float:
        return len(n1_neighbors & n2_neighbors) / len(n1_neighbors | n2_neighbors)

    @staticmethod
    def jaccard_index_npy(n1_neighbors: np.array, n2_neighbors: np.array) -> float:
        return len(np.intersect1d(n1_neighbors, n2_neighbors)) / len(np.union1d(n1_neighbors, n2_neighbors))

    def most_similar_to_group(self, opinion_ids: set) -> Dict[str, float]:
        opinion_neighbor_sets = [set(self.citation_network.network.neighbors(opinion_id)) for opinion_id in opinion_ids]
        similarity_value_dict = {}
        for node in self.citation_network.network.nodes:
            if node in opinion_ids:
                continue
            other_node_edges = set(self.citation_network.network.neighbors(node))
            similarity_value_dict[node] = \
                sum(self.jaccard_index(op_neighbors, other_node_edges) for op_neighbors in opinion_neighbor_sets) \
                / len(opinion_neighbor_sets)
        return similarity_value_dict

    def most_similar_to_group_npy(self, opinion_ids: set) -> Dict[str, float]:
        pass

    def internal_similarity(self, opinion_ids: set) -> nx.Graph:
        """
        Returns the internal similarity relationships in a group of cases.
        """
        neighbor_dict = {oi: set(self.citation_network.network.neighbors(oi)) for oi in opinion_ids}
        output_graph = nx.complete_graph(opinion_ids)

        for id_1, id_2 in output_graph.edges:
            output_graph[id_1][id_2]['weight'] = \
                self.jaccard_index(neighbor_dict[id_1], neighbor_dict[id_2])
        return output_graph

    def most_similar_cases(self, opinion_id) -> Dict[str, float]:
        opinion_neighbors = set(self.citation_network.network.neighbors(opinion_id))
        similarity_value_dict = {}
        for node in opinion_neighbors:
            other_node_edges = set(self.citation_network.network.neighbors(node))
            similarity_value_dict[node] = self.jaccard_index(opinion_neighbors, other_node_edges)
        return similarity_value_dict

    @staticmethod
    @cache
    def db_case_similarity(cases: frozenset, max_cases=25):
        """Instead of the network approach, uses cached similarity indexes in the database
        to calculate similarity with a SQL query."""
        similarity_alias = 'average_similarity'
        query = Similarity \
            .select(Similarity.opinion_b, (fn.SUM(Similarity.similarity_index) / len(cases)).alias(similarity_alias)) \
            .join(Opinion, on=Similarity.opinion_b) \
            .join(Cluster) \
            .where(Similarity.opinion_a << cases) \
            .group_by(Similarity.opinion_b) \
            .order_by(SQL(similarity_alias).desc()) \
            .limit(max_cases)
        return query
