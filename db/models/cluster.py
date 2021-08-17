from enum import Enum
from peewee import IntegerField, TextField, fn
from playhouse.postgres_ext import TSVectorField
from db.models import BaseModel


class Court:
    SCOTUS = 'scotus'
    CA1 = 'ca1'
    CA2 = 'ca2'
    CA3 = 'ca3'
    CA4 = 'ca4'
    CA5 = 'ca5'
    CA6 = 'ca6'
    CA7 = 'ca7'
    CA8 = 'ca8'
    CA9 = 'ca9'
    CA10 = 'ca10'
    CA11 = 'ca11'
    CADC = 'cadc'
    CAFC = 'cafc'


class Cluster(BaseModel):
    resource_id = IntegerField()
    case_name = TextField()
    reporter = TextField(null=True)
    court = TextField(null=True)
    citation_count = IntegerField()
    cluster_uri = TextField()
    docket_uri = TextField()
    year = IntegerField()
    time = IntegerField()
    searchable_case_name = TSVectorField()

    @staticmethod
    def case_display_name():
        """Plaintiff v. Defendant, Reporter (Year), written in query syntax."""
        return fn.CONCAT(Cluster.case_name, fn.coalesce(fn.CONCAT(', ', Cluster.reporter)), ' (', Cluster.year, ')')
