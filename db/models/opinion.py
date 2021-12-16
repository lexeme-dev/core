from typing import List, Optional
from peewee import IntegerField, TextField, ForeignKeyField
from db.models import BaseModel, Cluster


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    html_text = TextField(null=True)
    cluster = ForeignKeyField(Cluster, field='resource_id', backref='opinion')

    parentheticals: Optional[List[str]]
