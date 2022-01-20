from typing import List, Optional
from peewee import IntegerField, TextField, ForeignKeyField
from db.peewee.models import BaseModel, Cluster


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    html_text = TextField(null=True)
    cluster = ForeignKeyField(Cluster, field='resource_id', backref='opinion')

    parentheticals: Optional[List[str]]
    contexts: Optional[List[str]]

    def ingest_parenthetical(parenthetical):
        """ Someday we may not want to just append """
        self.parentheticals.append(parenthetical)

    def ingest_context(context):
        """ Someday we may not want to just append """
        self.contexts.append(context)
