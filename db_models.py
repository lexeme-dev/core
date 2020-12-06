from peewee import *

db = SqliteDatabase('data/db/scotus_data.db')

class BaseModel(Model):
    class Meta:
        database = db


class Cluster(BaseModel):
    resource_id = IntegerField()
    case_name = TextField()
    citation_count = IntegerField()
    cluster_uri = TextField()
    docket_uri = TextField()


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    cluster = ForeignKeyField(Cluster, field='resource_id', backref='opinions')


class Citation(BaseModel):
    citing_opinion = ForeignKeyField(Opinion, field='resource_id', backref='citations')
    cited_opinion = ForeignKeyField(Opinion, field='resource_id', backref='citations')
    depth = IntegerField()