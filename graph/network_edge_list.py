from typing import NamedTuple, Dict, Iterable
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.orm import contains_eager

from db.sqlalchemy import get_session
from db.sqlalchemy.models import *


class NodeMetadata(NamedTuple):
    start: int
    end: int
    length: int
    year: int


class NetworkEdgeList:
    """
    An alternative representation of a network that is optimized for random sampling of neighbors
    """
    edge_list: np.array
    node_metadata: Dict[int, NodeMetadata]

    def __init__(self, scotus_only):
        opinion_query = self.__init_queries(scotus_only)
        self.__populate_edge_list(opinion_query)

    def __init_queries(self, scotus_only):
        with get_session() as s:
            edge_list_size = s.execute(select(func.count(Citation.id))).scalar() * 2
            self.edge_list = np.empty(edge_list_size, dtype='int32')
            self.node_metadata = {}
            opinion_query = (select(Opinion)
                             .join(Opinion.citations)
                             .options(contains_eager(Opinion.citations)))
            if scotus_only:
                opinion_query = Citation.where_court(opinion_query, citing_court=Court.SCOTUS, cited_court=Court.SCOTUS)
            opinion_query = opinion_query.order_by(Citation.citing_opinion_id, Citation.cited_opinion_id)
            return s.execute(opinion_query).unique().scalars().all()

    def __populate_edge_list(self, opinion_iter: Iterable[Opinion]):
        prev_index = 0
        for opinion in opinion_iter:
            num_neighbors = len(opinion.citations)
            node_neighbors = np.empty(num_neighbors, dtype='int32')
            for i, citation in enumerate(opinion.citations):
                if citation.cited_opinion_id == opinion.resource_id:
                    neighbor = citation.citing_opinion_id
                else:
                    neighbor = citation.cited_opinion_id
                node_neighbors[i] = neighbor
            start_idx = prev_index
            end_idx = start_idx + len(node_neighbors)
            year = None
            try:
                year = opinion.cluster.year
            except:
                pass
            self.node_metadata[opinion.resource_id] = NodeMetadata(start=start_idx, end=end_idx,
                                                                   length=len(node_neighbors), year=year)
            self.edge_list[start_idx:end_idx] = node_neighbors
            prev_index = end_idx
