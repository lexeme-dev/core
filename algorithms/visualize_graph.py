from graph.citation_network import CitationNetwork
import networkx as nx
import matplotlib.pyplot as plt
from db.db_models import Opinion

resource_id = 100014
plt.figure(figsize=(20, 20), frameon=False)

bbox = dict(alpha=0.25)

citation_graph = CitationNetwork.construct_network()
roe_ego = nx.ego_graph(citation_graph, resource_id, 1)
centrality = nx.eigenvector_centrality(roe_ego)
top_opinions = [opinion_id for opinion_id, centrality_score in sorted(centrality.items(), key=lambda item: item[1], reverse=True)][:40]
output_str = ""
name_map = {}
for i, opinion_id in enumerate(top_opinions):
    try:
        opinion = Opinion.get(Opinion.resource_id == opinion_id)
        name: str = opinion.cluster.case_name
        name_arr = name.split("v. ")
        name_arr[0] = " ".join(name_arr[0].split(" ")[:3]) if len(name_arr[0]) > 25 else name_arr[0]
        name_arr[1] = " ".join(name_arr[1].split(" ")[:3]) if len(name_arr[1]) > 25 else name_arr[1]
        name_arr.insert(1, " v. \n")
        name_map[opinion.resource_id] = "".join(name_arr)
        output_str += f'{i + 1}: {opinion.resource_id}, {opinion.cluster.case_name}\n'
    except:
        name_map[opinion_id] = "Unknown"
        pass
print(output_str)
top_opinion_names = [name_map[op] for op in top_opinions]
subgraph = nx.subgraph(roe_ego, top_opinions)
subgraph = nx.relabel_nodes(subgraph, name_map)
graph_pos = nx.shell_layout(subgraph, [top_opinion_names[:5], top_opinion_names[5:10], top_opinion_names[10:15], top_opinion_names[15:]])
nx.draw_networkx_nodes(subgraph, graph_pos, node_size=100)
nx.draw_networkx_edges(subgraph, graph_pos, width=0.6, edge_color="#585858")
nx.draw_networkx_labels(subgraph, graph_pos, font_size=16, font_family="Georgia", font_weight="bold", bbox=bbox)

plt.axis('off')
axis = plt.gca()
axis.set_xlim([1.15*x for x in axis.get_xlim()])
axis.set_ylim([1.15*y for y in axis.get_ylim()])
plt.tight_layout()
plt.savefig(f"output/ego-plot-{name_map[resource_id].split(' v.')[0].strip()}.png")
plt.show()
