from peewee import ForeignKeyField, IntegerField
from db.models import BaseModel, Cluster


class ClusterCitation(BaseModel):
    citing_cluster = ForeignKeyField(Cluster, field='resource_id', backref='clustercitation', lazy_load=False)
    cited_cluster = ForeignKeyField(Cluster, field='resource_id', backref='clustercitation', lazy_load=False)
    depth = IntegerField()
