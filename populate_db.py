import os
import json
import csv
from db_models import db, Cluster, Opinion, Citation
import peewee as pw


def create_db_tables(db: pw.SqliteDatabase):
    db.create_tables([Cluster, Opinion, Citation])


def ingest_cluster_data(db, clusters_dir):
    cluster_records = []
    directory = os.fsencode(clusters_dir)
    for file in os.listdir(directory):
        try:
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                file_path = os.path.join(clusters_dir, filename)
                with open(file_path, encoding="utf8") as json_file:
                    cluster_data = json.load(json_file)
                    new_record = Cluster(resource_id=cluster_data['id'],
                                         case_name=cluster_data['case_name'],
                                         cluster_uri=cluster_data['resource_uri'],
                                         docket_uri=cluster_data['docket'],
                                         citation_count=cluster_data['citation_count'])
                    cluster_records.append(new_record)
        except:
            print(f'Failure on file {file}')
    with db.atomic():
        Cluster.bulk_create(cluster_records, batch_size=100)


def ingest_opinion_data(db: pw.SqliteDatabase, opinions_dir):
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


def ingest_citation_data(db, citations_file):
    # Since there's only ~65,000 opinions, it's feasible to just load all the IDs into memory to avoid making millions of DB queries.
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
    create_db_tables(db)
    ingest_cluster_data(db, r"data/scotus_clusters/")
    ingest_opinion_data(db, r"data/scotus_opinions/")
    ingest_citation_data(db, r"data/citations.csv")
    db.close()
