import csv
import json
from collections import defaultdict
from typing import DefaultDict, List
from uuid import uuid4

from datasketch import MinHash, MinHashLSH
from nltk import bigrams, wordpunct_tokenize

from utils.io import get_full_path

with open(get_full_path("data/parentheticals/bell_parentheticals_cl.json")) as f:
    parentheticals = json.load(f)

id_text_dict = dict()
id_hash_dict = dict()
counter = 1
lsh = MinHashLSH(threshold=0.5, num_perm=128)
for text in parentheticals:
    text_bigrams = [" ".join(words) for words in bigrams(wordpunct_tokenize(text))]
    mhash = MinHash(num_perm=128)
    mhash.update_batch([gram.encode("utf-8") for gram in text.split()])
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


print("Breakpoint here")
