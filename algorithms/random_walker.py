from random import randrange
from graph import CitationNetwork


class RandomWalker:
    citation_network: CitationNetwork

    def __init__(self, citation_network):
        self.citation_network = citation_network

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
        node_info = self.citation_network.network_edge_list.node_metadata[source_node]
        if node_info.start == node_info.end:
            return source_node
        return self.citation_network.network_edge_list.edge_list[randrange(node_info.start, node_info.end)]
