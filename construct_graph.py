import networkx as nx
from db_models import db, Citation, Opinion

MAX_DEPTH = 122  # To normalize lowest edge weight to 1


def construct_graph():
    citation_graph = nx.Graph()
    db.connect()
    citations = [(c.citing_opinion, c.cited_opinion, c.depth / MAX_DEPTH) for c in Citation.select()]
    db.close()
    citation_graph.add_weighted_edges_from(citations)
    return citation_graph
