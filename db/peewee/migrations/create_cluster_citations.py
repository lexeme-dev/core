"""
For our current use cases, the Citation table can be kind of cumbersome because we don't actually care about
individual opinions (plus, CourtListener's data about individual opinions is extremely unreliable), so
I'm creating a new table based on the existing Citation data which directly uses Cluster IDs.
"""
from db.peewee.models import *

if __name__ == '__main__':
    # db.create_tables([ClusterCitation])
    CitingOpinion, CitedOpinion = Opinion.alias(), Opinion.alias()
    CitingCluster, CitedCluster = Cluster.alias(), Cluster.alias()
    existing_citations_query = Citation.select(Citation, CitingOpinion, CitedOpinion, CitingCluster, CitedCluster) \
        .join_from(Citation, CitingOpinion, on=Citation.citing_opinion) \
        .join_from(Citation, CitedOpinion, on=Citation.cited_opinion) \
        .join_from(CitingOpinion, CitingCluster) \
        .join_from(CitedOpinion, CitedCluster)
    print(existing_citations_query)
    cluster_citation_dict = {}  # Key: tuple of citing cluster ID, cited cluster ID; value: ClusterCitation model
    i = 0
    for citation in existing_citations_query:
        i += 1
        if i % 1000 == 0:
            print("Current citation number:", i)
        citing_cluster, cited_cluster = citation.citing_opinion.cluster, citation.cited_opinion.cluster
        identifier_tuple = citing_cluster.resource_id, cited_cluster.resource_id
        if identifier_tuple in cluster_citation_dict:
            cluster_citation_dict[identifier_tuple].depth += citation.depth
        cluster_citation_dict[identifier_tuple] = \
            ClusterCitation(citing_cluster=citing_cluster, cited_cluster=cited_cluster, depth=citation.depth)
    ClusterCitation.bulk_create(list(cluster_citation_dict.values()), batch_size=1000)
