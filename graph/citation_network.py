from typing import Dict
import networkx as nx
import numpy as np
from sklearn.cluster import DBSCAN
from db.db_models import db, Citation
import graph.case_similarity

MAX_DEPTH = 122  # To normalize lowest edge weight to 1


class CitationNetwork:
    network: nx.Graph
    similarity: graph.case_similarity.CitationNetworkSimilarity

    def __init__(self, directed=False):
        self.network = self.construct_network(directed)
        self.similarity = graph.case_similarity.CitationNetworkSimilarity(self.network)

    @staticmethod
    def construct_network(directed=False):
        if directed:
            citation_network = nx.DiGraph()
        else:
            citation_network = nx.Graph()
        db.connect()
        citations = [(c.citing_opinion, c.cited_opinion, 1 / c.depth) for c in Citation.select()]
        db.close()
        citation_network.add_weighted_edges_from(citations)
        return citation_network

    def cluster(self, opinion_ids: set, eps=0.94) -> Dict[int, set]:
        cases = opinion_ids
        sgraph = self.similarity.internal_similarity(cases)
        slaplacian = nx.laplacian_matrix(sgraph).toarray()
        slaplacian += 1
        sdist = slaplacian * (1 - np.identity(slaplacian.shape[0]))
        labels = DBSCAN(eps=eps, min_samples=1, metric="precomputed") \
                .fit(sdist) \
                .labels_
        output = {}
        for c, l in zip(cases, labels):
            if not l in output:
                output[l] = set()
            output[l].add(c)
        return output
