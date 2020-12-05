from peewee import *
from typing import List
import os
import json

db = SqliteDatabase('data/db/scotus_data.db')


class BaseModel(Model):
    class Meta:
        database = db


class Cluster(BaseModel):
    resource_id = IntegerField()
    case_name = TextField()
    citation_count = IntegerField()
    cluster_uri = TextField()
    docket_uri = TextField()


class Opinion(BaseModel):
    resource_id = IntegerField()
    opinion_uri = TextField()
    cluster_uri = TextField()
    cluster = ForeignKeyField(Cluster, field='resource_id', backref='opinions')


def create_db_tables(db: SqliteDatabase):
    db.create_tables([Cluster, Opinion])


def ingest_cluster_data(db, clusters_dir):
    cluster_records: List[Cluster] = []
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


def ingest_opinion_data(db: SqliteDatabase, opinions_dir):
    opinion_records: List[Opinion] = []
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


if __name__ == '__main__':
    db.connect()
    create_db_tables(db)
    ingest_cluster_data(db, r"data/scotus_clusters/")
    ingest_opinion_data(db, r"data/scotus_opinions/")
    db.close()
