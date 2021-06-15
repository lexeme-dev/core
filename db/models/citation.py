from peewee import ForeignKeyField, IntegerField
from db.models import BaseModel, Opinion


class Citation(BaseModel):
    citing_opinion = ForeignKeyField(Opinion, field='resource_id', backref='out_citations', lazy_load=False)
    cited_opinion = ForeignKeyField(Opinion, field='resource_id', backref='in_citations', lazy_load=False)
    depth = IntegerField()
