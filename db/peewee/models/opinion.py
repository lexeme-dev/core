from typing import List, Optional
from peewee import IntegerField, TextField, ForeignKeyField
from db.peewee.models import BaseModel, Cluster


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    html_text = TextField(null=True)
    cluster = ForeignKeyField(Cluster, field="resource_id", backref="opinion")

    parentheticals: Optional[List[str]]
    contexts: Optional[List[str]]

    def ingest_parentheticals(self, parenthetical):
        """Someday we may not want to just append"""
        try:
            self.parentheticals.append(parenthetical)
        except AttributeError:
            self.parentheticals = []
            self.parentheticals.append(parenthetical)

    def ingest_contexts(self, context):
        """Someday we may not want to just append"""
        try:
            self.contexts.append(context)
        except AttributeError:
            self.contexts = []
            self.contexts.append(context)
