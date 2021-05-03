from flask import Flask, jsonify, abort, request
from http import HTTPStatus
from db.db_models import Opinion, Cluster, Similarity
from graph.citation_network import CitationNetwork
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
citation_graph = CitationNetwork()


@app.route('/cases/<int:resource_id>')
def get_case(resource_id: int):
    try:
        opinion = Opinion.get(resource_id=resource_id)
        return model_to_dict(opinion)
    except Opinion.DoesNotExist:
        abort(HTTPStatus.NOT_FOUND)


@app.route('/cases/similar')
def similar_cases_to_group():
    case_resource_ids = request.args.getlist('cases')
    if len(case_resource_ids) < 1:
        return "You must provide at least one case ID.", HTTPStatus.UNPROCESSABLE_ENTITY
    similar_case_query = citation_graph.similarity.db_case_similarity(tuple(case_resource_ids))
    similar_cases = [similarity_record.opinion_b for similarity_record in similar_case_query]
    return jsonify(list(map(model_to_dict, similar_cases)))


@app.route('/search')
def search():
    return {
        "name": "Faiz",
        "job": "Useful idiot"
    }
