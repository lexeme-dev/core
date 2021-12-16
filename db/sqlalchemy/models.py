# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Integer, Text, Sequence, Index, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger, Sequence('citation_seq'), primary_key=True)
    citing_opinion_id = Column(BigInteger)
    cited_opinion_id = Column(BigInteger)
    depth = Column(BigInteger)

    # We have to do these rather than index=True on the column because our previous ORM named indexes by its own convention
    # and for backwards compatibility reasons we're not going to recreate them with SQLAlchemy's default names.
    # When adding new columns in the future, this is unnecessary, just use index=True
    __table_args__ = (
        Index('idx_40711_citation_citing_opinion_id', 'citing_opinion_id', unique=False),
        Index('idx_40711_citation_cited_opinion_id', 'cited_opinion_id', unique=False),
    )


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
    searchable_case_name = Column(TSVECTOR)
    court = Column(Text)

    __table_args__ = (
        Index('searchable_case_name_idx', 'searchable_case_name', unique=False),
    )


class ClusterCitation(Base):
    __tablename__ = 'clustercitation'

    id = Column(BigInteger, Sequence('clustercitation_seq'), primary_key=True)
    citing_cluster_id = Column(BigInteger)
    cited_cluster_id = Column(BigInteger)
    depth = Column(BigInteger)

    __table_args__ = (
        Index('idx_40753_clustercitation_citing_cluster_id', 'citing_cluster_id', unique=False),
        Index('idx_40753_clustercitation_cited_cluster_id', 'cited_cluster_id', unique=False),
    )


class Opinion(Base):
    __tablename__ = 'opinion'

    id = Column(BigInteger, Sequence('opinion_seq'), primary_key=True)
    resource_id = Column(BigInteger)
    opinion_uri = Column(Text)
    cluster_uri = Column(Text)
    cluster_id = Column(BigInteger)
    html_text = Column(Text)

    __table_args__ = (
        Index('idx_40705_opinion_cluster_id', 'cluster_id', unique=False),
    )


class OpinionParenthetical(Base):
    __tablename__ = 'opinionparenthetical'

    # This column has a different integer type and sequence naming convention, would be good to fix in the future
    id = Column(Integer, Sequence('opinionparenthetical_id_seq'), primary_key=True)
    citing_opinion_id = Column(Integer, nullable=False)
    cited_opinion_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    # The convention for index naming changes again. Why?
    __table_args__ = (
        Index('opinionparenthetical_citing_opinion_id', 'citing_opinion_id', unique=False),
        Index('opinionparenthetical_cited_opinion_id', 'cited_opinion_id', unique=False),
    )


class Similarity(Base):
    __tablename__ = 'similarity'

    id = Column(BigInteger, Sequence('similarity_seq'), primary_key=True)
    opinion_a_id = Column(BigInteger)
    opinion_b_id = Column(BigInteger)
    similarity_index = Column(Float)

    __table_args__ = (
        Index('idx_40750_similarity_opinion_a_id', 'opinion_a_id', unique=False),
        Index('idx_40750_similarity_opinion_b_id', 'opinion_b_id', unique=False),
    )
