import networkx as nx
from helpers import top_n
from construct_graph import construct_graph
from typing import Set, Dict

citation_graph: nx.Graph


def jaccard_index(n1_neighbors: Set[str], n2_neighbors: Set[str]) -> float:
    return len(n1_neighbors & n2_neighbors) / len(n1_neighbors | n2_neighbors)


def most_similar_cases(opinion_id) -> Dict[str, float]:
    opinion_edges = set(citation_graph.neighbors(opinion_id))
    similarity_value_dict = {}
    for node in (opinion_edges | {opinion_id}):
        other_node_edges = set(citation_graph.neighbors(node))
        similarity_value_dict[node] = jaccard_index(opinion_edges, other_node_edges)
    return similarity_value_dict


opinion = 118144  # Hurley v. Irish American
print(top_n(most_similar_cases(opinion), 25))
