from peewee import IntegerField, TextField, fn
from playhouse.postgres_ext import TSVectorField
from db.models import BaseModel


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
