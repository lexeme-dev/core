import pickle
import os
import networkx as nx
from db.models import db, Citation
from graph.network_edge_list import NetworkEdgeList
from helpers import get_full_path

CITATION_CSV_PATH = 'data/citation_list.csv'
NETWORK_CACHE_PATH = 'tmp/network_cache.pik'


class CitationNetwork:
    network: nx.Graph
    network_edge_list: NetworkEdgeList

    def __init__(self, directed=False):
        self.network = self.construct_network(directed)
        self.network_edge_list = NetworkEdgeList()

    @staticmethod
    def get_citation_network(enable_caching=True):
        cache_file_path = get_full_path(NETWORK_CACHE_PATH)
        if not enable_caching:
            return CitationNetwork()
        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, 'rb') as cache_file:
                    return pickle.load(cache_file)
            except BaseException as err:
                print("Loading citation network from cache file failed with error:", err)
                return CitationNetwork()  # Create a new network if fetching from cache fails
        else:  # Otherwise, construct a new network and cache it.
            new_network = CitationNetwork()
            try:
                with open(cache_file_path, 'wb') as cache_file:
                    pickle.dump(new_network, cache_file)
            except BaseException as err:
                print("Saving citation network to cache file failed with error:", err)
            return new_network

    @staticmethod
    def construct_network(directed=False):
        if directed:
            citation_network = nx.DiGraph()
        else:
            citation_network = nx.Graph()
        citations = [(c.citing_opinion, c.cited_opinion, c.depth) for c in Citation.select()]
        citation_network.add_weighted_edges_from(citations)
        return citation_network
