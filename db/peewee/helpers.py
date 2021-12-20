import os
from typing import List
from dotenv import load_dotenv
from flask import jsonify
from peewee import Expression, PostgresqlDatabase, Model
from playhouse.shortcuts import model_to_dict


def ts_match(vector, query):
    return Expression(vector, '@@', query)


def connect_to_database():
    load_dotenv()
    db_host, db_name, db_username, db_password, db_port = (os.getenv('DB_HOST'), os.getenv('DB_NAME'),
                                                           os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'),
                                                           os.getenv('DB_PORT'))
    return PostgresqlDatabase(db_name, user=db_username, password=db_password, host=db_host, port=db_port)


def model_list_to_json(peewee_models: List[Model], **kwargs):
    return jsonify(model_list_to_dicts(peewee_models, **kwargs))


def model_list_to_dicts(peewee_models: List[Model], **kwargs):
    from db.peewee.models import DEFAULT_SERIALIZATION_ARGS

    return list(map(lambda model: model_to_dict(model, **DEFAULT_SERIALIZATION_ARGS, **kwargs), peewee_models))
