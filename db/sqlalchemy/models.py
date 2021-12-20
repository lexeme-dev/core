# coding: utf-8
from enum import Enum
from typing import Tuple
from sqlalchemy import BigInteger, Column, Float, Integer, Text, Sequence, Index, ForeignKey, String
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, aliased, relationship, deferred
from sqlalchemy.sql import Alias

Base = declarative_base()
metadata = Base.metadata


class Court(str, Enum):
    SCOTUS = 'scotus'
    CA1 = 'ca1'
    CA2 = 'ca2'
    CA3 = 'ca3'
    CA4 = 'ca4'
    CA5 = 'ca5'
    CA6 = 'ca6'
    CA7 = 'ca7'
    CA8 = 'ca8'
    CA9 = 'ca9'
    CA10 = 'ca10'
    CA11 = 'ca11'
    CADC = 'cadc'
    CAFC = 'cafc'


class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger, Sequence('citation_seq'), primary_key=True)
    citing_opinion_id = Column(BigInteger, ForeignKey('opinion.resource_id'), index=True)
    cited_opinion_id = Column(BigInteger, ForeignKey('opinion.resource_id'), index=True)
    depth = Column(BigInteger)

    # noinspection PyPep8Naming
    @staticmethod
    def join_to_clusters(base_citation_query: Query) -> Tuple[Query, Alias, Alias]:
        citing_opinion, cited_opinion = aliased(Opinion), aliased(Opinion)
        citing_cluster, cited_cluster = aliased(Cluster), aliased(Cluster)
        return (base_citation_query
                .join(citing_opinion, Citation.citing_opinion_id == citing_opinion.resource_id)
                .join(cited_opinion, Citation.cited_opinion_id == cited_opinion.resource_id)
                .join(citing_cluster, citing_opinion.cluster_id == citing_cluster.resource_id)
                .join(cited_cluster, cited_opinion.cluster_id == cited_cluster.resource_id)
                ), citing_cluster, cited_cluster

    @staticmethod
    def where_court(base_citation_query: Query, citing_court: Court = None,
                    cited_court: Court = None) -> Query:
        citation_query, citing_cluster_alias, cited_cluster_alias = Citation.join_to_clusters(base_citation_query)
        if citing_court and cited_court:
            citation_query = (citation_query.filter((citing_cluster_alias.court == citing_court) &
                                                    (cited_cluster_alias.court == cited_court)))
        elif citing_court:
            citation_query = citation_query.filter(citing_cluster_alias.court == citing_court)
        elif cited_court:
            citation_query = citation_query.filter(cited_cluster_alias.court == cited_court)
        return citation_query


class Cluster(Base):
    __tablename__ = 'cluster'

    id = Column(BigInteger, Sequence('cluster_seq'), primary_key=True)
    resource_id = Column(BigInteger, index=True, unique=True)
    case_name = Column(Text)
    reporter = Column(Text)
    citation_count = Column(BigInteger)
    cluster_uri = Column(Text)
    docket_uri = Column(Text)
    year = Column(BigInteger)
    time = Column(BigInteger)
    searchable_case_name = Column(TSVECTOR)
    court = Column(Text)
    courtlistener_json_checksum = Column(String(32))

    __table_args__ = (
        Index('searchable_case_name_idx', 'searchable_case_name', postgresql_using='gin', unique=False),
    )


class ClusterCitation(Base):
    __tablename__ = 'clustercitation'

    id = Column(BigInteger, Sequence('clustercitation_seq'), primary_key=True)
    citing_cluster_id = Column(BigInteger, ForeignKey('cluster.resource_id'), index=True)
    cited_cluster_id = Column(BigInteger, ForeignKey('cluster.resource_id'), index=True)
    depth = Column(BigInteger)


class Opinion(Base):
    __tablename__ = 'opinion'

    id = Column(BigInteger, Sequence('opinion_seq'), primary_key=True)
    resource_id = Column(BigInteger, index=True, unique=True)
    opinion_uri = Column(Text)
    cluster_uri = Column(Text)
    cluster_id = Column(BigInteger, ForeignKey('cluster.resource_id'))
    cluster = relationship("Cluster", lazy='joined')
    html_text = deferred(Column(Text))
    courtlistener_json_checksum = Column(String(32))

    out_citations = relationship("Citation", primaryjoin="Opinion.resource_id == Citation.citing_opinion_id",
                                 backref="citing_opinion")
    in_citations = relationship("Citation", primaryjoin="Opinion.resource_id == Citation.cited_opinion_id",
                                backref="cited_opinion")
    citations = relationship("Citation",
                             primaryjoin="or_(Opinion.resource_id == Citation.cited_opinion_id, Opinion.resource_id == Citation.citing_opinion_id)",
                             overlaps="citing_opinion,cited_opinion,in_citations,out_citations")


class OpinionParenthetical(Base):
    __tablename__ = 'opinionparenthetical'

    # This column has a different integer type and sequence naming convention, would be good to fix in the future
    id = Column(Integer, Sequence('opinionparenthetical_id_seq'), primary_key=True)
    citing_opinion_id = Column(Integer, ForeignKey('opinion.resource_id'), index=True, nullable=False)
    cited_opinion_id = Column(Integer, ForeignKey('opinion.resource_id'), index=True, nullable=False)
    text = Column(Text, nullable=False)


class Similarity(Base):
    __tablename__ = 'similarity'

    id = Column(BigInteger, Sequence('similarity_seq'), primary_key=True)
    opinion_a_id = Column(BigInteger, ForeignKey('opinion.resource_id'), index=True)
    opinion_b_id = Column(BigInteger, ForeignKey('opinion.resource_id'), index=True)
    similarity_index = Column(Float)
