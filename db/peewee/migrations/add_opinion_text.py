import os
import json
from playhouse.migrate import *
from db.peewee.models import *
from utils.io import get_full_path

HTML_TEXT_FIELDS = ['html_with_citations', 'html', 'html_lawbox', 'html_columbia', 'html_anon_2020', 'plain_text']


def add_opinion_text_col():
    html_text_field = TextField(null=True)
    migrator = PostgresqlMigrator(db)
    migrate(
        migrator.add_column('opinion', 'html_text', html_text_field)
    )


def populate_opinion_text(opinions_dir):
    def get_html_text(opinion_data):
        for field in HTML_TEXT_FIELDS:
            if opinion_data.get(field) and len(opinion_data[field]) > 0:
                return opinion_data[field]
        return None

    batch = 0
    opinions = Opinion.select().order_by(Opinion.resource_id).limit(1000)
    dir_files = {os.fsdecode(filename) for filename in os.listdir(os.fsencode(opinions_dir))}
    while opinions.count() > 0:
        for opinion in opinions:
            json_filename = f"{opinion.resource_id}.json"
            if json_filename not in dir_files:
                print(f"Could not find json for opinion ID {opinion.resource_id}")
                continue
            json_file_path = os.path.join(opinions_dir, json_filename)
            with open(json_file_path, encoding='utf8', mode='r') as opinion_json_file:
                opinion_data = json.load(opinion_json_file)
                opinion.html_text = get_html_text(opinion_data)
                if opinion.html_text is None:
                    print(f"{opinion.resource_id} has no html_text")
        Opinion.bulk_update(opinions, fields=[Opinion.html_text], batch_size=100)
        batch += 1
        print(f"Finished adding text for {batch * 1000} opinions...")
        opinions = Opinion.select().order_by(Opinion.resource_id).offset(batch * 1000).limit(1000)


if __name__ == '__main__':
    add_opinion_text_col()
    populate_opinion_text(get_full_path(r'data/scotus_opinions'))
