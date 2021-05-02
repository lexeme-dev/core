from flask import Flask, jsonify, abort
from db.db_models import Opinion, Cluster
from graph.citation_network import CitationNetwork
from functools import lru_cache
from helpers import top_n
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
citation_graph = CitationNetwork()


@app.route('/cases/<int:resource_id>')
def get_case(resource_id: int):
    try:
        opinion = Opinion.get(resource_id=resource_id)
        return model_to_dict(opinion)
    except Opinion.DoesNotExist:
        abort(404)


@lru_cache(maxsize=None)
@app.route('/cases/<int:resource_id>/similar')
def similar_cases(resource_id: int):
    similar_case_dict = top_n(citation_graph.similarity.most_similar_cases(resource_id), 25)
    query = Opinion.select().join(Cluster).where(Opinion.resource_id << list(similar_case_dict))
    similar_cases = sorted(query, key=lambda op: similar_case_dict[op.resource_id], reverse=True)
    return jsonify(list(map(model_to_dict, similar_cases)))


@app.route('/search')
def search():
    return {
        "name": "Faiz",
        "job": "Useful idiot"
    }
