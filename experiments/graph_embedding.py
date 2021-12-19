import networkx as nx
from nodevectors import Node2Vec

from graph import CitationNetwork
from helpers import get_full_path

citation_network = CitationNetwork.get_citation_network(enable_caching=True)
G = citation_network.network

# Fit embedding model to graph
g2v = Node2Vec(
    n_components=32,
    walklen=5,
    epochs=50
)
# way faster than other node2vec implementations
# Graph edge weights are handled automatically
g2v.fit(G)

# query embeddings for node 42
g2v.predict(117960)

# Save and load whole node2vec model
# Uses a smart pickling method to avoid serialization errors
# Don't put a file extension after the `.save()` filename, `.zip` is automatically added
g2v.save(get_full_path('data/embeddings/node2vec'))
# You however need to specify the extension when reading it back
g2v = Node2Vec.load(get_full_path('data/embeddings/node2vec.zip'))

# Save model to gensim.KeyedVector format
g2v.save_vectors(get_full_path("data/embeddings/wheel_model.bin"))

# load in gensim
# from gensim.models import KeyedVectors
# model = KeyedVectors.load_word2vec_format(get_full_path("data/embeddings/wheel_model.bin"))
