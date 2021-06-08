from typing import List, Optional
from peewee import IntegerField, TextField, ForeignKeyField, FloatField, fn
from playhouse.postgres_ext import TSVectorField
from playhouse.signals import Model
from helpers import connect_to_database

db = connect_to_database()


class BaseModel(Model):
    class Meta:
        database = db


class Cluster(BaseModel):
    resource_id = IntegerField()
    case_name = TextField()
    reporter = TextField(null=True)
    citation_count = IntegerField()
    cluster_uri = TextField()
    docket_uri = TextField()
    year = IntegerField()
    time = IntegerField()
    searchable_case_name = TSVectorField()

    @staticmethod
    def case_display_name():
        """Plaintiff v. Defendant, Reporter (Year), written in query syntax."""
        return fn.CONCAT(Cluster.case_name, fn.coalesce(fn.CONCAT(', ', Cluster.reporter)), ' (', Cluster.year, ')')


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    html_text = TextField(null=True)
    cluster = ForeignKeyField(Cluster, field='resource_id', backref='opinion')

    parentheticals: Optional[List[str]]


class Citation(BaseModel):
    citing_opinion = ForeignKeyField(Opinion, field='resource_id', backref='out_citations', lazy_load=False)
    cited_opinion = ForeignKeyField(Opinion, field='resource_id', backref='in_citations', lazy_load=False)
    depth = IntegerField()


class Similarity(BaseModel):
    opinion_a = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    opinion_b = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    similarity_index = FloatField()


class ClusterCitation(BaseModel):
    citing_cluster = ForeignKeyField(Cluster, field='resource_id', backref='clustercitation', lazy_load=False)
    cited_cluster = ForeignKeyField(Cluster, field='resource_id', backref='clustercitation', lazy_load=False)
    depth = IntegerField()


DEFAULT_SERIALIZATION_ARGS = {
    "exclude": [Cluster.searchable_case_name, Opinion.html_text],
}
