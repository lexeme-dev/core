from flask import Flask, abort, request, jsonify
from flask_cors import CORS
from http import HTTPStatus
from graph import CitationNetwork
from db.models import Opinion, Cluster, DEFAULT_SERIALIZATION_ARGS
from playhouse.shortcuts import model_to_dict
from helpers import model_list_to_json, model_list_to_dicts
from algorithms import CaseSearch, CaseClustering, CaseRecommendation, CaseSimilarity
from extraction.pdf_engine import PdfEngine
from extraction.citation_extractor import CitationExtractor
from io import BufferedReader
import oyez_brief

app = Flask(__name__)
CORS(app)
citation_network = CitationNetwork.get_citation_network(enable_caching=True)
similarity = CaseSimilarity(citation_network)
clustering = CaseClustering(citation_network)
recommendation = CaseRecommendation(citation_network)


@app.after_request
def configure_caching(response: Flask.response_class):
    response.cache_control.max_age = 300
    return response


# TODO: If necessary (because extraction and parsing is slow), we can implement this as a stateful background job.
@app.route('/pdf/upload', methods=['POST'])
def upload_pdf():
    file = request.files.get('file')
    if file is None:
        return "No file provided.", HTTPStatus.UNPROCESSABLE_ENTITY
    pdf_text = PdfEngine(BufferedReader(file)).get_text()
    citations = list(CitationExtractor(pdf_text).get_extracted_citations())
    return model_list_to_json(citations, extra_attrs=['parentheticals'])


# TODO: All of these /cases/ routes can be refactored into their own Flask blueprint
@app.route('/cases/<int:resource_id>')
def get_case(resource_id: int):
    try:
        opinion = Opinion.get(resource_id=resource_id)
        return model_to_dict(opinion, **DEFAULT_SERIALIZATION_ARGS)
    except Opinion.DoesNotExist:
        abort(HTTPStatus.NOT_FOUND)


@app.route('/cases/similar')
def get_similar_cases():
    case_resource_ids = request.args.getlist('cases')
    max_cases = request.args.get('max_cases')
    if len(case_resource_ids) < 1:
        return "You must provide at least one case ID.", HTTPStatus.UNPROCESSABLE_ENTITY
    similar_case_query = similarity.db_case_similarity(frozenset(case_resource_ids), max_cases)
    similar_cases = [similarity_record.opinion_b for similarity_record in similar_case_query]
    return model_list_to_json(similar_cases)


@app.route('/cases/recommendations')
def get_recommended_cases():
    case_resource_ids = frozenset(map(int, request.args.getlist('cases')))
    max_cases = int(request.args.get('max_cases') or 10)
    if len(case_resource_ids) < 1:
        return "You must provide at least one case ID.", HTTPStatus.UNPROCESSABLE_ENTITY
    recommendations = recommendation.recommendations(case_resource_ids, max_cases)
    recommended_opinions = sorted(
        Opinion.select().join(Cluster).where(Opinion.resource_id << list(recommendations.keys())),
        key=lambda op: recommendations[op.resource_id],
        reverse=True
    )
    return model_list_to_json(recommended_opinions)


@app.route('/cases/search')
def search():
    search_query = request.args.get('query')
    max_cases = request.args.get('max_cases')
    if search_query is None or len(search_query) == 0:
        return jsonify([])
    search_results = CaseSearch.search_cases(search_query, max_cases=max_cases)
    return model_list_to_json(search_results, extra_attrs=['headline'])


@app.route('/cases/<int:resource_id>/oyez_brief')
def get_oyez_brief(resource_id: int):
    if brief := oyez_brief.from_resource_id(resource_id):
        return brief._asdict()
    abort(HTTPStatus.NOT_FOUND)


@app.route('/cases/cluster')
def get_case_clusters():
    case_resource_ids = [int(c) for c in request.args.getlist('cases')]
    num_clusters = int(request.args.get('num_clusters') or 0) or None
    if len(case_resource_ids) < 1:
        return "You must provide at least one case ID.", HTTPStatus.UNPROCESSABLE_ENTITY
    clusters = clustering.spectral_cluster(set(case_resource_ids), num_clusters=num_clusters)
    output_dict = {}
    for cluster_name, opinion_ids in clusters.items():
        opinion_models = Opinion.select().where(Opinion.resource_id << opinion_ids)
        output_dict[str(cluster_name)] = model_list_to_dicts(opinion_models)
    return output_dict
