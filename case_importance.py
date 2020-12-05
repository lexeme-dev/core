import networkx as nx
import csv
import peewee as pw

citation_graph = nx.Graph()

with open('data/citations.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        elif line_count < 100_000:
            edge_weight = 1 / float(row[2])
            citation_graph.add_edge(row[0], row[1], weight=edge_weight)
            line_count += 1
        else:
            break
    print(f'Processed {line_count} lines.')

print(citation_graph.number_of_edges())
print(citation_graph.number_of_nodes())
centrality = nx.eigenvector_centrality(citation_graph)
sorted_centrality = sorted((v, f"{c:0.2f}") for v, c in centrality.items())
print("Done")
