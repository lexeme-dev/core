from peewee import Model
from db.peewee.helpers import connect_to_database

db = connect_to_database()


class BaseModel(Model):
    class Meta:
        database = db
