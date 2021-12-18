# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Integer, Text, Sequence, Index, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, aliased, relationship, deferred

Base = declarative_base()
metadata = Base.metadata


class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger, Sequence('citation_seq'), primary_key=True)
    citing_opinion_id = Column(BigInteger, ForeignKey('opinion.resource_id'), index=True)
    cited_opinion_id = Column(BigInteger, ForeignKey('opinion.resource_id'), index=True)
    depth = Column(BigInteger)


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

    __table_args__ = (
        Index('searchable_case_name_idx', 'searchable_case_name', unique=False),
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
