from functools import cache
import networkx as nx
from typing import Set, Dict
from db.db_models import Similarity, Opinion, Cluster
from peewee import SQL, fn


class CaseSimilarity:
    network: nx.Graph

    def __init__(self, network):
        self.network = network

    @staticmethod
    def jaccard_index(n1_neighbors: Set[str], n2_neighbors: Set[str]) -> float:
        return len(n1_neighbors & n2_neighbors) / len(n1_neighbors | n2_neighbors)

    def most_similar_to_group(self, opinion_ids: set) -> Dict[str, float]:
        opinion_neighbor_sets = [set(self.network.neighbors(opinion_id)) for opinion_id in opinion_ids]
        similarity_value_dict = {}
        for node in self.network.nodes:
            if node in opinion_ids:
                continue
            other_node_edges = set(self.network.neighbors(node))
            similarity_value_dict[node] = \
                sum(self.jaccard_index(op_neighbors, other_node_edges) for op_neighbors in opinion_neighbor_sets) \
                / len(opinion_neighbor_sets)
        return similarity_value_dict

    def internal_similarity(self, opinion_ids: set) -> nx.Graph:
        """
        Returns the internal similarity relationships in a group of cases.
        """
        neighbor_dict = {oi: set(self.network.neighbors(oi)) for oi in opinion_ids}
        output_graph = nx.complete_graph(opinion_ids)

        for id_1, id_2 in output_graph.edges:
            output_graph[id_1][id_2]['weight'] = \
                self.jaccard_index(neighbor_dict[id_1], neighbor_dict[id_2])
        return output_graph

    def most_similar_cases(self, opinion_id) -> Dict[str, float]:
        opinion_neighbors = set(self.network.neighbors(opinion_id))
        similarity_value_dict = {}
        for node in opinion_neighbors:
            other_node_edges = set(self.network.neighbors(node))
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


if __name__ == "__main__":
    from graph.citation_network import CitationNetwork
    citation_graph = CitationNetwork()
    # opinion = 118144  # Hurley v. Irish American
    # print(top_n(most_similar_cases(opinion), 25))
    ISSUE_1_2020_CASES = {103870, 107637, 105294, 117960, 117869, 118139, 4288403}
    ISSUE_1_2021_CASES = {103716, 106950, 108326, 117927, 118363, 118370, 799995, 809122}
    ISSUE_2_2021_CASES = {107082, 96230, 101076, 104943, 112478, 112786, 118144, 130160, 2812209, 799995}

    similarity = citation_graph.similarity.db_case_similarity(frozenset(ISSUE_1_2020_CASES))
    a = list(similarity)
    print("\n".join(sim.case_name for sim in similarity))
    # print("\n".join(get_names_for_id_collection(
    #     top_n(citation_graph.similarity.most_similar_to_group(ISSUE_1_2021_CASES), 25)
    # )))
