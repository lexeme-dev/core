from db_models import db, Similarity
from graph.citation_network import CitationNetwork

if __name__ == "__main__":
    db.create_tables([Similarity])
    citation_network = CitationNetwork()
    similarity_objects = []
    total_num_nodes, num_nodes_completed = citation_network.network.number_of_nodes(), 0
    for node in citation_network.network.nodes:
        node_similarity_indexes = citation_network.similarity.most_similar_cases(node)
        similarity_objects.extend(Similarity(opinion_a=node, opinion_b=key, similarity_index=value)
                                  for key, value in node_similarity_indexes.items())
        with db.atomic():
            Similarity.bulk_create(similarity_objects, batch_size=1000)
            num_nodes_completed += 1
            print("{} nodes processed, {:.1%} ".format(num_nodes_completed, num_nodes_completed / total_num_nodes))
