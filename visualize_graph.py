from construct_graph import construct_graph
import networkx as nx
import matplotlib.pyplot as plt


citation_graph = construct_graph()
nx.draw(citation_graph)
plt.show()