import numpy as np
from itertools import chain
from db.db_models import *
from peewee import prefetch


class NetworkEdgeList:
    """
    An alternative representation of a network that is optimized for random sampling of neighbors
    """
    edge_list: np.array
    node_metadata: dict

    def __init__(self):
        edge_list_size = Citation.select().count() * 2
        self.edge_list = np.empty(edge_list_size, dtype='int32')
        self.node_metadata = {}
        prev_index = 0
        opinion_query = Opinion.select(Opinion.resource_id)
        citation_query = Citation.select(Citation.citing_opinion_id, Citation.cited_opinion_id, Citation.depth)
        prefetch(opinion_query, citation_query)
        for opinion in opinion_query:
            num_neighbors = len(opinion.out_citations) + len(opinion.in_citations)
            node_neighbors = np.empty(num_neighbors, dtype='int32')
            for i, citation in enumerate(chain(opinion.out_citations, opinion.in_citations)):
                if citation.cited_opinion_id == opinion.resource_id:
                    neighbor = citation.citing_opinion_id
                else:
                    neighbor = citation.cited_opinion_id
                node_neighbors[i] = neighbor
            start_idx = prev_index
            end_idx = start_idx + len(node_neighbors)
            self.node_metadata[opinion.resource_id] = {'start': start_idx, 'end': end_idx, 'length': end_idx - start_idx}
            self.edge_list[start_idx:end_idx] = node_neighbors
            prev_index = end_idx
