from peewee import Model
from helpers import connect_to_database

deebee = connect_to_database()


class BaseModel(Model):
    class Meta:
        database = deebee
