import csv

from peewee import chunked
from db.peewee.models import *
from utils.io import get_full_path


def drop_existing_citations():
    # VERY SCARY!!!
    Citation.delete().execute()


def get_citation_iterable():
    csv_file = open(get_full_path(r"data/citations.csv"), 'r')
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)  # Skip header row
    return csv_reader


def add_all_citations_for_current_cases(citation_iterable, opinion_ids):
    citations_to_create = []
    for row in citation_iterable:
        citing_op_id, cited_op_id, depth = int(row[0]), int(row[1]), int(row[2])
        if citing_op_id in opinion_ids and cited_op_id in opinion_ids:
            citations_to_create.append({
                'citing_opinion_id': citing_op_id,
                'cited_opinion_id': cited_op_id,
                'depth': depth
            })
    print('Finished reading CSV, beginning DB write...')
    i = 1
    for batch in chunked(citations_to_create, 10000):
        print(f'Wrote {i * 10000} rows')
        Citation.insert_many(batch).execute()


opinion_resource_ids = {op.resource_id for op in Opinion.select(Opinion.resource_id)}
print('Fetched opinion IDs...')
with db.atomic():
    drop_existing_citations()
    print('Dropped existing citations...')
    citation_iterable = get_citation_iterable()
    print('Opened CSV file...')
    add_all_citations_for_current_cases(citation_iterable, opinion_resource_ids)
