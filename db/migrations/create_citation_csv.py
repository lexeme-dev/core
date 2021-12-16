from db.models import *
from helpers import get_full_path
import csv

CITATION_CSV_PATH = 'data/citation_list.csv'

if __name__ == '__main__':
    citations = Citation.select(Citation.citing_opinion, Citation.cited_opinion, Citation.depth)
    with open(get_full_path(CITATION_CSV_PATH), 'w') as citation_file:
        csv_writer = csv.writer(citation_file)
        for citation in citations:
            csv_writer.writerow((citation.citing_opinion, citation.cited_opinion, citation.depth))
