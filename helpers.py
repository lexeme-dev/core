import heapq
from collections import OrderedDict
from typing import Dict
from db_models import db, Opinion, Cluster


def get_names_for_id_collection(collection):
    names = []
    for op_id in collection:
        try:
            name = Opinion.get(Opinion.resource_id == op_id).cluster.case_name
            names.append(name)
        except:
            names.append("Unknown")
    return names


def top_n(value_dict: dict, n: int) -> Dict[str, float]:
    """Helper function to find the n highest-value keys in a dictionary.
    Runs in O(n+k) time for a dictionary with k entries."""
    # Have to reformat the dict like this for heapq to cooperate.
    collection = [(value, key) for key, value in value_dict.items()]
    heapq.heapify(collection)
    top_n_items = OrderedDict()
    for nth_largest in heapq.nlargest(n, collection):
        top_n_items[nth_largest[1]] = nth_largest[0]  # Reconstruct the dict
    return top_n_items
