from construct_graph import CitationGraph
import networkx as nx
import pickle
from helpers import get_names_for_id_collection

from graphrole import RecursiveFeatureExtractor, RoleExtractor

citation_graph = CitationGraph.construct_network()
feature_extractor = RecursiveFeatureExtractor(citation_graph)
features = feature_extractor.extract_features()
role_extractor = RoleExtractor(n_roles=None)
role_extractor.extract_role_factors(features)
node_roles = role_extractor.roles

print('\nNode role assignments:')
print(node_roles)

print('\nNode role membership by percentage:')
print(role_extractor.role_percentage.round(2))
# TODO: When I come back to this, use the debugger console to save the generated data structures to disk (using pickle, I believe)
print("Done.")

# with open("data/role_data.pik", "wb") as f:
#     pickle.dump({"citation_graph": citation_graph, "feature_extractor": feature_extractor, "features": features,
#                  "role_extractor": role_extractor, "node_roles": node_roles, "role_percentages":
#                      role_extractor.role_percentage.round(2)}, f, -1)
