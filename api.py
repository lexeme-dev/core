from flask import Flask, jsonify, abort
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
        abort(404)


@app.route('/cases/<int:resource_id>/similar')
def similar_cases(resource_id: int):
    get_case(resource_id)
    query = Similarity.select() \
        .join(Opinion, on=Similarity.opinion_b).join(Cluster) \
        .where(Similarity.opinion_a == resource_id) \
        .order_by(Similarity.similarity_index.desc()) \
        .limit(25)
    similar_cases = [similarity_record.opinion_b for similarity_record in query]
    return jsonify(list(map(model_to_dict, similar_cases)))


@app.route('/search')
def search():
    return {
        "name": "Faiz",
        "job": "Useful idiot"
    }
