import pickle
import os
import networkx as nx
from gensim.models.keyedvectors import Word2VecKeyedVectors, KeyedVectors
from sqlalchemy import select

from db.sqlalchemy import get_session
from db.sqlalchemy.models import Citation, Court
from graph.network_edge_list import NetworkEdgeList
from utils.io import NETWORK_CACHE_PATH, N2V_MODEL_PATH
from utils.logger import Logger


class CitationNetwork:
    network: nx.Graph
    network_edge_list: NetworkEdgeList
    n2v_model: Word2VecKeyedVectors

    def __init__(self, directed=False, scotus_only=False):
        # self.network = self.construct_network(directed, scotus_only)
        self.network_edge_list = NetworkEdgeList(scotus_only)
        self.n2v_model = self.get_n2v_model()

    @staticmethod
    def get_citation_network(enable_caching=True, scotus_only=False):
        if not enable_caching:
            Logger.info("Creating citation network from database...")
            return CitationNetwork(scotus_only=scotus_only)
        if os.path.exists(NETWORK_CACHE_PATH):
            Logger.info("Loading citation network from disk cache...")
            try:
                with open(NETWORK_CACHE_PATH, 'rb') as cache_file:
                    return pickle.load(cache_file)
            except BaseException as err:
                Logger.error("Loading citation network from cache file failed with error:", err)
                Logger.info('Creating citation network from database...')
                return CitationNetwork(scotus_only=scotus_only)  # Create a new network if fetching from cache fails
        else:  # Otherwise, construct a new network and cache it.
            Logger.info('Creating citation network from database...')
            new_network = CitationNetwork(scotus_only=scotus_only)
            try:
                Logger.info('Writing network cache to disk...')
                with open(NETWORK_CACHE_PATH, 'wb') as cache_file:
                    pickle.dump(new_network, cache_file)
            except BaseException as err:
                Logger.info("Saving citation network to cache file failed with error:", err)
            return new_network

    @staticmethod
    def construct_network(directed, scotus_only):
        if directed:
            citation_network = nx.DiGraph()
        else:
            citation_network = nx.Graph()
        citation_query = select(Citation)
        if scotus_only:
            citation_query = Citation.where_court(citation_query, citing_court=Court.SCOTUS, cited_court=Court.SCOTUS)
        with get_session() as s:
            citations = [(c.citing_opinion_id, c.cited_opinion_id, c.depth) for c in s.execute(citation_query).scalars().all()]
        citation_network.add_weighted_edges_from(citations)
        return citation_network

    @staticmethod
    def get_n2v_model():
        Logger.info('Attempting to load N2V model...')
        if not os.path.exists(N2V_MODEL_PATH):
            Logger.warn('N2V model not found while initializing network, recommendations_n2v will error...')
            return
        return KeyedVectors.load_word2vec_format(N2V_MODEL_PATH)
