from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple, Dict, List
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.sqlalchemy import get_session
from db.sqlalchemy.models import *
from utils.logger import Logger


class NodeMetadata(NamedTuple):
    start: int
    end: int
    length: int
    year: int
    court: str


class NetworkEdgeList:
    """
    An alternative representation of a network that is optimized for random sampling of neighbors
    """
    scotus_only: bool
    edge_list: np.array
    node_metadata: Dict[int, NodeMetadata]
    session: Session | None

    def __init__(self, scotus_only):
        Logger.info('Initializing network edge list...')
        self.scotus_only = scotus_only
        self.session = get_session()  # At some point we will get better session management, pinky promise.
        neighbor_dict = self.__get_neighbor_dict()
        self.__populate_edge_list_and_metadata(neighbor_dict)
        self.session.close()
        self.session = None

    def __get_neighbor_dict(self) -> Dict[int, List[int]]:
        edge_query = select(Citation.citing_opinion_id, Citation.cited_opinion_id)
        if self.scotus_only:
            edge_query = Citation.where_court(edge_query, citing_court=Court.SCOTUS, cited_court=Court.SCOTUS)
        edges: List[Tuple[int, int]] = self.session.execute(edge_query).all()
        opinion_neighbor_dict: Dict[int, List[int]] = defaultdict(list)
        for (citing, cited) in edges:
            opinion_neighbor_dict[citing].append(cited)
            opinion_neighbor_dict[cited].append(citing)
        # Kind of a dumb place to initialize this but we have the number of edges here so may as well.
        self.edge_list = np.empty(len(edges) * 2, dtype='int32')
        return opinion_neighbor_dict

    def __populate_edge_list_and_metadata(self, neighbor_dict: Dict[int, List[int]]):
        self.node_metadata = {}
        opinion_year_query = select(Opinion.resource_id, Cluster.year).join(Opinion.cluster)
        opinion_court_query = select(Opinion.resource_id, Cluster.court).join(Opinion.cluster)
        if self.scotus_only:
            opinion_year_query = opinion_year_query.filter(Cluster.court == Court.SCOTUS)
        opinion_year_dict = {op_id: year for op_id, year in
                             self.session.execute(opinion_year_query).all()}
        opinion_court_dict = {op_id: court for op_id, court in
                              self.session.execute(opinion_court_query).all()}
        prev_index = 0
        for opinion_id, neighbors in neighbor_dict.items():
            start_idx = prev_index
            end_idx = start_idx + len(neighbors)
            self.node_metadata[opinion_id] = \
                NodeMetadata(
                    start=start_idx,
                    end=end_idx,
                    length=len(neighbors),
                    court=opinion_court_dict.get(opinion_id),
                    year=opinion_year_dict.get(opinion_id)
                )
            self.edge_list[start_idx:end_idx] = neighbors
            prev_index = end_idx
