from experiments import experiment_helpers
from graph.citation_network import CitationNetwork

if __name__ == '__main__':
    citation_network = CitationNetwork()
    print("Network initialized, beginning recommendation computation...")
    op_id = 118144
    print(experiment_helpers.opinion_ids_to_names([op_id]))
    recs = citation_network.recommendation.recommendations_for_case(op_id)
    sims = citation_network.similarity.db_case_similarity(frozenset([op_id]), max_cases=10)
    print(experiment_helpers.opinion_ids_to_names(recs.keys()))
    print([sim.opinion_b.cluster.case_name for sim in sims])
