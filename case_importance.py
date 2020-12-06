import networkx as nx
from db_models import db, Citation, Opinion

MAX_DEPTH = 122  # To normalize lowest edge weight to 1

citation_graph = nx.DiGraph()

db.connect()
citations = [(c.citing_opinion, c.cited_opinion, {'weight': MAX_DEPTH / c.depth}) for c in Citation.select()]
citation_graph.add_edges_from(citations)
print(citation_graph.number_of_edges())
print(citation_graph.number_of_nodes())

centrality = nx.in_degree_centrality(citation_graph)
top_opinions = [opinion_id for opinion_id, centrality_score in sorted(centrality.items(), key=lambda item: item[1], reverse=True)][:100]

output_str = ""
for i, opinion_id in enumerate(top_opinions):
    try:
        opinion = Opinion.get(Opinion.resource_id == opinion_id)
        output_str += f'{i + 1}: {opinion.cluster.case_name}\n'
    except:
        pass
print(output_str)
