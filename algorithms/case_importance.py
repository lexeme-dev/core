import networkx as nx
from db.peewee.models import db, Opinion
from graph.citation_network import CitationNetwork

citation_graph = CitationNetwork.construct_network()

centrality = nx.eigenvector_centrality_numpy(citation_graph)
top_opinions = [opinion_id for opinion_id, centrality_score in sorted(centrality.items(), key=lambda item: item[1], reverse=True)][:100]

db.connect()
output_str = ""
for i, opinion_id in enumerate(top_opinions):
    try:
        opinion = Opinion.get(Opinion.resource_id == opinion_id)
        output_str += f'{i + 1}: {opinion.resource_id}, {opinion.cluster.case_name}\n'
    except:
        pass
print(output_str)
