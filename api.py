from flask import Flask
from graph.construct_graph import construct_graph

app = Flask(__name__)
citation_graph = construct_graph()


@app.route('/search')
def search():
    return {
        "name": "Faiz",
        "job": "Useful idiot"
    }
