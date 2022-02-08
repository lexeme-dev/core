from typing import Tuple
from peewee import ForeignKeyField, IntegerField, ModelSelect, ModelAlias
from db.peewee.models import BaseModel, Opinion, Cluster, Court


class Citation(BaseModel):
    citing_opinion = ForeignKeyField(
        Opinion, field="resource_id", backref="out_citations", lazy_load=False
    )
    cited_opinion = ForeignKeyField(
        Opinion, field="resource_id", backref="in_citations", lazy_load=False
    )
    depth = IntegerField()

    # noinspection PyPep8Naming
    @staticmethod
    def join_to_clusters(
        base_citation_query: ModelSelect,
    ) -> Tuple[ModelSelect, ModelAlias, ModelAlias]:
        CitingOpinion, CitedOpinion = Opinion.alias(), Opinion.alias()
        CitingCluster, CitedCluster = Cluster.alias(), Cluster.alias()
        return (
            (
                base_citation_query.join_from(
                    Citation, CitingOpinion, on=Citation.citing_opinion
                )
                .join_from(Citation, CitedOpinion, on=Citation.cited_opinion)
                .join_from(CitingOpinion, CitingCluster)
                .join_from(CitedOpinion, CitedCluster)
            ),
            CitingCluster,
            CitedCluster,
        )

    @staticmethod
    def where_court(
        base_citation_query: ModelSelect,
        citing_court: Court = None,
        cited_court: Court = None,
    ) -> ModelSelect:
        (
            citation_query,
            citing_cluster_alias,
            cited_cluster_alias,
        ) = Citation.join_to_clusters(base_citation_query)
        if citing_court and cited_court:
            citation_query = citation_query.where(
                (citing_cluster_alias.court == citing_court)
                & (cited_cluster_alias.court == cited_court)
            )
        elif citing_court:
            citation_query = citation_query.where(
                citing_cluster_alias.court == citing_court
            )
        elif cited_court:
            citation_query = citation_query.where(
                cited_cluster_alias.court == cited_court
            )
        return citation_query
