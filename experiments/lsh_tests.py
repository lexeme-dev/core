import json
import re
from collections import defaultdict
from typing import DefaultDict, List
from uuid import uuid4

from datasketch import MinHash, MinHashLSH
from nltk import bigrams, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

from utils.io import get_full_path

with open(get_full_path("data/parentheticals/brady_parentheticals_cl.json")) as f:
    parentheticals = json.load(f)

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

id_text_dict = dict()
id_hash_dict = dict()
counter = 1
lsh = MinHashLSH(threshold=0.25, num_perm=128)
for text in parentheticals:
    mhash = MinHash(num_perm=128)
    cleaned_text = re.sub(r"[^A-Za-z0-9 ]+", "", text)

    tokens = [
        stemmer.stem(word)
        for word in word_tokenize(cleaned_text)
        if word not in stop_words
    ]
    print(" ".join(tokens))
    word_bigrams = [" ".join(gram) for gram in bigrams(tokens)]
    mhash.update_batch([gram.encode("utf-8") for gram in word_bigrams])
    text_id = uuid4().hex
    id_text_dict[text_id] = text
    id_hash_dict[text_id] = mhash
    lsh.insert(text_id, mhash)
    counter += 1


similarity_graph: DefaultDict[str, list] = defaultdict(list)
for id, mhash in id_hash_dict.items():
    similarity_graph[id].extend(lsh.query(mhash))


clusters: List[List[str]] = []
visited = set()


def get_component(node, graph, visited) -> List[str]:
    current_cluster = []
    if node not in visited:
        visited.add(node)
        current_cluster.append(node)
        for neighbor in graph[node]:
            current_cluster.extend(get_component(neighbor, graph, visited))
    return current_cluster


for node, neighbors in similarity_graph.items():
    if current_cluster := get_component(node, similarity_graph, visited):
        clusters.append(current_cluster)

text_clusters = []
for cluster in clusters:
    text_clusters.append([id_text_dict[id] for id in cluster])
text_clusters.sort(key=lambda cl: len(cl), reverse=True)

for cl in text_clusters:
    print(f"{cl[0]} - {len(cl)}")

print("Breakpoint here")
