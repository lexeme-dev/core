import heapq
import os.path
from math import inf
from collections import OrderedDict
from typing import Dict
from dotenv import load_dotenv
from typing import List
from flask import jsonify
from peewee import Model, PostgresqlDatabase
from playhouse.shortcuts import model_to_dict


def top_n(value_dict: dict, n: int) -> Dict[str, float]:
    """Helper function to find the n highest-value keys in a dictionary.
    Runs in O(n+k) time for a dictionary with k entries."""
    if n is None or n == inf:
        return value_dict
    # Have to reformat the dict like this for heapq to cooperate.
    collection = [(value, key) for key, value in value_dict.items()]
    heapq.heapify(collection)
    top_n_items = OrderedDict()
    for nth_largest in heapq.nlargest(n, collection):
        top_n_items[nth_largest[1]] = nth_largest[0]  # Reconstruct the dict
    return top_n_items


def get_full_path(relative_project_path):
    load_dotenv()
    return os.path.join(os.getenv('PROJECT_PATH'), relative_project_path)


def connect_to_database():
    load_dotenv()
    db_host, db_name, db_username, db_password, db_port = (os.getenv('DB_HOST'), os.getenv('DB_NAME'),
                                                           os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'),
                                                           os.getenv('DB_PORT'))
    return PostgresqlDatabase(db_name, user=db_username, password=db_password, host=db_host, port=db_port)


def model_list_to_json(peewee_models: List[Model], **kwargs):
    return jsonify(model_list_to_dicts(peewee_models, **kwargs))


def model_list_to_dicts(peewee_models: List[Model], **kwargs):
    from db.db_models import DEFAULT_SERIALIZATION_ARGS

    return list(map(lambda model: model_to_dict(model, **DEFAULT_SERIALIZATION_ARGS, **kwargs), peewee_models))


def format_reporter(volume, reporter, page):
    return f"{volume} {reporter} {page}"
