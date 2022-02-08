import os

import csrgraph
from nodevectors import Node2Vec

from ingress.create_citations_csv import create_citations_csv
from utils.logger import Logger


class EmbeddingTrainer:
    model_path: str
    csv_path: str

    def __init__(self, model_path, csv_path):
        self.model_path = model_path
        self.csv_path = csv_path

    def train(self):
        graph = self.__get_csr_graph()
        Logger.info("Training node2vec embeddings...")
        g2v = Node2Vec(n_components=32, walklen=8, epochs=25)
        g2v.fit(graph)
        Logger.info(f"Training done. Saving embeddings to {self.model_path}")
        g2v.save_vectors(self.model_path)

    def __get_csr_graph(self) -> csrgraph.csrgraph:
        if not os.path.exists(self.csv_path):
            Logger.info("Couldn't find citation CSV, generating from database...")
            create_citations_csv()
        Logger.info("Initializing CSR graph for embedding training...")
        return csrgraph.read_edgelist(self.csv_path, directed=False, sep=",")
