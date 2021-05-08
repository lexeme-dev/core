from peewee import IntegerField, TextField, ForeignKeyField, FloatField
from playhouse.sqlite_ext import SqliteExtDatabase, FTS5Model, SearchField
from playhouse.signals import Model
from helpers import get_full_path

db = SqliteExtDatabase(get_full_path('data/db/scotus_data2.db'))


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


class SearchableCase(BaseModel, FTS5Model):
    case_name = SearchField()
    reporter = SearchField()
    year = SearchField()
    opinion_id = SearchField(unindexed=True)
    cluster_id = SearchField(unindexed=True)
