from peewee import IntegerField, TextField, ForeignKeyField, FloatField
from playhouse.sqlite_ext import FTS5Model, SearchField
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


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    cluster = ForeignKeyField(Cluster, field='resource_id', backref='opinion')


class Citation(BaseModel):
    citing_opinion = ForeignKeyField(Opinion, field='resource_id', backref='citation', lazy_load=False)
    cited_opinion = ForeignKeyField(Opinion, field='resource_id', backref='citation', lazy_load=False)
    depth = IntegerField()


class Similarity(BaseModel):
    opinion_a = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    opinion_b = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    similarity_index = FloatField()


class SearchableCase(FTS5Model):
    class Meta:
        database = db

    case_name = SearchField()
    reporter = SearchField()
    year = SearchField()
    opinion_id = SearchField(unindexed=True)
    cluster_id = SearchField(unindexed=True)


class ClusterCitation(BaseModel):
    citing_cluster = ForeignKeyField(Cluster, field='resource_id', backref='clustercitation', lazy_load=False)
    cited_cluster = ForeignKeyField(Cluster, field='resource_id', backref='clustercitation', lazy_load=False)
    depth = IntegerField()
