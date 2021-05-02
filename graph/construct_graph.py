import networkx as nx
from db.db_models import db, Citation
from graph import case_similarity

MAX_DEPTH = 122  # To normalize lowest edge weight to 1


class CitationGraph:
    network: nx.Graph
    similarity: case_similarity.CitationGraphSimilarity

    def __init__(self, directed=False):
        self.network = self.construct_network(directed)
        self.similarity = case_similarity.CitationGraphSimilarity(self.network)

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
