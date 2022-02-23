from nodevectors import Node2Vec, GGVec
import csrgraph as cg
from nodevectors.evaluation import link_pred

from utils.io import get_full_path
from ingress.create_citations_csv import CITATION_CSV_PATH, create_citations_csv
import os

csv_path = get_full_path(CITATION_CSV_PATH)
if not os.path.exists(csv_path):
    print("Couldn't find citation CSV, generating from database...")
    create_citations_csv()


# G = cg.read_edgelist(csv_path, directed=False, sep=",")

# Fit embedding model to graph
# g2v = GGVec(n_components=64, threads=4)
# way faster than other node2vec implementations
# Graph edge weights are handled automatically
# g2v.fit(G)

# query embeddings for node 42
# g2v.predict(117960)

# Save and load whole node2vec model
# Uses a smart pickling method to avoid serialization errors
# Don't put a file extension after the `.save()` filename, `.zip` is automatically added
# g2v.save(get_full_path("data/embeddings/ggvec"))
# You however need to specify the extension when reading it back
g2v = GGVec.load(get_full_path('data/embeddings/ggvec.zip'))

print("")
# Save model to gensim.KeyedVector format
# g2v.save_vectors(get_full_path("data/embeddings/node2vec_model.bin"))

# load in gensim
# from gensim.models import KeyedVectors
# model = KeyedVectors.load_word2vec_format(get_full_path("data/embeddings/wheel_model.bin"))
