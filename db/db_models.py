from peewee import *

db = SqliteDatabase('../data/db/scotus_data2.db')


class BaseModel(Model):
    class Meta:
        database = db


class Cluster(BaseModel):
    resource_id = IntegerField()
    case_name = TextField()
    citation_count = IntegerField()
    cluster_uri = TextField()
    docket_uri = TextField()
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
