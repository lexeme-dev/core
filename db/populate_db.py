import os
import json
import csv
import dateutil.parser
from datetime import timezone
from db_models import db, Cluster, Opinion, Citation, SearchableCase
from helpers import get_full_path


def create_db_tables():
    db.create_tables([Cluster, Opinion, Citation, SearchableCase])


def get_reporter(cluster_data):
    reporters = cluster_data.get('citations')
    if reporters is None or len(reporters) == 0:
        return None
    reporter_to_use = reporters[0]
    for reporter in reporters[1:]:
        if reporter['reporter'] == 'U.S.':
            reporter_to_use = reporter
            break
    return f"{reporter_to_use['volume']} {reporter_to_use['reporter']} {reporter_to_use['page']}"


def ingest_cluster_data(clusters_dir):
    cluster_records = []
    directory = os.fsencode(clusters_dir)
    for file in os.listdir(directory):
        try:
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                file_path = os.path.join(clusters_dir, filename)
                with open(file_path, encoding="utf8") as json_file:
                    cluster_data = json.load(json_file)
                    date_filed = dateutil.parser.parse(cluster_data['date_filed']).replace(tzinfo=timezone.utc)
                    reporter = get_reporter(cluster_data)
                    new_record = Cluster(resource_id=cluster_data['id'],
                                         case_name=cluster_data['case_name'],
                                         cluster_uri=cluster_data['resource_uri'],
                                         docket_uri=cluster_data['docket'],
                                         citation_count=cluster_data['citation_count'],
                                         reporter=reporter,
                                         year=date_filed.year,
                                         time=int(date_filed.timestamp()))
                    cluster_records.append(new_record)
        except:
            print(f'Failure on file {file}')
    with db.atomic():
        Cluster.bulk_create(cluster_records, batch_size=100)


def ingest_opinion_data(opinions_dir):
    opinion_records = []
    directory = os.fsencode(opinions_dir)
    for file in os.listdir(directory):
        try:
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                file_path = os.path.join(opinions_dir, filename)
                with open(file_path, encoding="utf8") as json_file:
                    opinion_data = json.load(json_file)
                    cluster_uri = opinion_data['cluster']
                    cluster_id = int(cluster_uri.split('/')[-2])
                    new_record = Opinion(resource_id=opinion_data['id'],
                                         opinion_uri=opinion_data['resource_uri'],
                                         cluster_uri=cluster_uri,
                                         cluster=cluster_id)
                    opinion_records.append(new_record)
        except:
            print(f'Failure on file {file}')
    with db.atomic():
        Opinion.bulk_create(opinion_records, batch_size=100)


def ingest_citation_data(citations_file):
    # Since there's only ~65,000 opinions, it's feasible to just load all the IDs into memory to avoid making
    # millions of DB queries.
    opinion_set = {o.resource_id for o in Opinion.select()}

    citation_records = []
    with open(citations_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            try:
                integer_row = [int(cell) for cell in row]
                if integer_row[0] in opinion_set and integer_row[1] in opinion_set:
                    new_record = Citation(citing_opinion=integer_row[0], cited_opinion=integer_row[1], depth=integer_row[2])
                    citation_records.append(new_record)
            except Exception as e:
                print(f'Failure on row {row}: {e}')
        with db.atomic():
            Citation.bulk_create(citation_records, batch_size=100)


if __name__ == '__main__':
    db.connect()
    create_db_tables()
    ingest_cluster_data(r"data/scotus_clusters/")
    ingest_opinion_data(r"data/scotus_opinions/")
    ingest_citation_data(r"data/citations.csv")
    db.close()
