# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Integer, Text, Sequence, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger, Sequence('citation_seq'), primary_key=True)
    citing_opinion_id = Column(BigInteger, index=True)
    cited_opinion_id = Column(BigInteger, index=True)
    depth = Column(BigInteger)


class Cluster(Base):
    __tablename__ = 'cluster'

    id = Column(BigInteger, Sequence('cluster_seq'), primary_key=True)
    resource_id = Column(BigInteger)
    case_name = Column(Text)
    reporter = Column(Text)
    citation_count = Column(BigInteger)
    cluster_uri = Column(Text)
    docket_uri = Column(Text)
    year = Column(BigInteger)
    time = Column(BigInteger)
    searchable_case_name = Column(TSVECTOR, index=True)
    court = Column(Text)


class ClusterCitation(Base):
    __tablename__ = 'clustercitation'

    id = Column(BigInteger, Sequence('clustercitation_seq'), primary_key=True)
    citing_cluster_id = Column(BigInteger, index=True)
    cited_cluster_id = Column(BigInteger, index=True)
    depth = Column(BigInteger)


class Opinion(Base):
    __tablename__ = 'opinion'

    id = Column(BigInteger, Sequence('opinion_seq'), primary_key=True)
    resource_id = Column(BigInteger)
    opinion_uri = Column(Text)
    cluster_uri = Column(Text)
    cluster_id = Column(BigInteger, index=True)
    html_text = Column(Text)


class OpinionParenthetical(Base):
    __tablename__ = 'opinionparenthetical'

    # This column has a different integer type and sequence naming convention, would be good to fix in the future
    id = Column(Integer, Sequence('opinionparenthetical_id_seq'), primary_key=True)
    citing_opinion_id = Column(Integer, nullable=False, index=True)
    cited_opinion_id = Column(Integer, nullable=False, index=True)
    text = Column(Text, nullable=False)


class Similarity(Base):
    __tablename__ = 'similarity'

    id = Column(BigInteger, Sequence('similarity_seq'), primary_key=True)
    opinion_a_id = Column(BigInteger, index=True)
    opinion_b_id = Column(BigInteger, index=True)
    similarity_index = Column(Float)
