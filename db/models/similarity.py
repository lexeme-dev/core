from peewee import ForeignKeyField, FloatField
from db.models import Opinion, BaseModel


class Similarity(BaseModel):
    opinion_a = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    opinion_b = ForeignKeyField(Opinion, field='resource_id', backref='citation')
    similarity_index = FloatField()
