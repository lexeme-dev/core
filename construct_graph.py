import networkx as nx
from db_models import db, Citation, Opinion
import pickle

MAX_DEPTH = 122  # To normalize lowest edge weight to 1


def construct_graph(directed=False):
    if directed:
        citation_graph = nx.DiGraph()
    else:
        citation_graph = nx.Graph()
    db.connect()
    citations = [(c.citing_opinion, c.cited_opinion, 1 / c.depth) for c in Citation.select()]
    db.close()
    citation_graph.add_weighted_edges_from(citations)
    return citation_graph
