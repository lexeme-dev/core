from peewee import *
import os

# TODO: The path to this db is all fucked up and has to be changed depending on where the main script is run. Fix it.
db_path = os.path.join(os.path.dirname(__name__), 'data/db/scotus_data2.db')
db = SqliteDatabase(db_path)


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


class Similarity(BaseModel):
    opinion_a = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    opinion_b = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    similarity_index = FloatField()
