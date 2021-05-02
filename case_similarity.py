import networkx as nx
from helpers import top_n, get_names_for_id_collection
from construct_graph import construct_graph
from typing import Set, Dict

citation_graph: nx.Graph


def jaccard_index(n1_neighbors: Set[str], n2_neighbors: Set[str]) -> float:
    return len(n1_neighbors & n2_neighbors) / len(n1_neighbors | n2_neighbors)


def most_similar_to_group(opinion_ids: set) -> Dict[str, float]:
    opinion_neighbor_sets = [set(citation_graph.neighbors(opinion_id)) for opinion_id in opinion_ids]
    similarity_value_dict = {}
    for node in citation_graph.nodes:
        if node in opinion_ids:
            continue
        other_node_edges = set(citation_graph.neighbors(node))
        similarity_value_dict[node] = \
            sum(jaccard_index(op_neighbors, other_node_edges) for op_neighbors in opinion_neighbor_sets) \
            / len(opinion_neighbor_sets)
    return similarity_value_dict


def most_similar_cases(opinion_id) -> Dict[str, float]:
    opinion_neighbors = set(citation_graph.neighbors(opinion_id))
    similarity_value_dict = {}
    for node in (opinion_neighbors | {opinion_id}):
        other_node_edges = set(citation_graph.neighbors(node))
        similarity_value_dict[node] = jaccard_index(opinion_neighbors, other_node_edges)
    return similarity_value_dict


citation_graph = construct_graph()
# opinion = 118144  # Hurley v. Irish American
# print(top_n(most_similar_cases(opinion), 25))
ISSUE_1_2020_CASES = {103870, 107637, 105294, 117960, 117869, 118139, 4288403}
ISSUE_1_2021_CASES = {103716, 106950, 108326, 117927, 118363, 118370, 799995, 809122}
ISSUE_2_2021_CASES = {107082, 96230, 101076, 104943, 112478, 112786, 118144, 130160, 2812209, 799995}

print("\n".join(get_names_for_id_collection(top_n(most_similar_to_group(ISSUE_1_2021_CASES), 25))))
