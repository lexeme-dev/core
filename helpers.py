import heapq
from collections import OrderedDict
from typing import Dict
from dotenv import load_dotenv
import os.path


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


def get_full_path(relative_project_path):
    load_dotenv()
    return os.path.join(os.getenv('PROJECT_PATH'), relative_project_path)