from db_models import db, Opinion
from construct_graph import construct_graph
from networkx.algorithms import community

citation_graph = construct_graph()
partitions = community.k_clique_communities(citation_graph, 50)
print("")
