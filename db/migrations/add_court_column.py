import os
import json
from playhouse.migrate import *
from db.models import *
from helpers import get_full_path

HTML_TEXT_FIELDS = ['html_with_citations', 'html', 'html_lawbox', 'html_columbia', 'html_anon_2020', 'plain_text']


def add_court_col():
    court = TextField()
    migrator = PostgresqlMigrator(db)
    migrate(
        migrator.add_column('cluster', 'court', court)
    )


def populate_court():
    Cluster.update({Cluster.court: "scotus"})

if __name__ == '__main__':
    add_court_col()
    populate_court()
