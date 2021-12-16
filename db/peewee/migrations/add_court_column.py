from playhouse.migrate import *
from db.peewee.models import *

HTML_TEXT_FIELDS = ['html_with_citations', 'html', 'html_lawbox', 'html_columbia', 'html_anon_2020', 'plain_text']


def add_court_col():
    court = TextField(null=True)
    migrator = PostgresqlMigrator(db)
    migrate(
        migrator.add_column('cluster', 'court', court)
    )


def populate_court():
    Cluster.update({Cluster.court: "scotus"}).execute()

if __name__ == '__main__':
    add_court_col()
    populate_court()
