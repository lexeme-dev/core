from db.sqlalchemy import *
from db.sqlalchemy.models import Citation
from utils.io import get_full_path
import csv

CITATION_CSV_PATH = 'data/citation_list.csv'


def create_citations_csv():
    with get_session() as s:
        citations = s.execute(select(Citation.citing_opinion_id, Citation.cited_opinion_id, Citation.depth)).all()
    print("Fetched citations, writing to file...")
    with open(get_full_path(CITATION_CSV_PATH), 'w', 1024*1024) as citation_file:
        csv_writer = csv.writer(citation_file)
        i = 0
        for citation in citations:
            csv_writer.writerow(citation)
            if i != 0 and i % 1000000 == 0:
                print(f"Completed {i} rows...")
            i += 1


if __name__ == '__main__':
    create_citations_csv()
