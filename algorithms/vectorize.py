from deebee.peewee.models import deebee, Citation, Opinion
import numpy as np

MAX_DEPTH = 122  # To normalize lowest edge weight to 1


def construct_mat():
    deebee.connect()
    citations = np.array([ \
        (c.citing_opinion, c.cited_opinion, c.depth) \
        for c in Citation.select()])
    deebee.close()
    # idk if this is the most efficient way to do this
    citing = np.unique(citations.T[0])
    cited = np.unique(citations.T[1])
    mat = np.zeros((len(citing), len(cited)))
    for ing, ed, depth in citations:
        mat[np.where(citing == ing)[0][0], np.where(cited == ed)[0][0]] += depth
    return mat, citing, cited


mat, citing, cited = construct_mat()


def nearest(resource_id):
    # Both scipy.spatial.kdtrees take too mcuh memory
    global citing
    global mat
    vec = mat[np.where(citing == resource_id)[0][0]]
    mat -= vec
    mat = np.linalg.norm(mat, axis=1)
    idx = np.argsort(mat)
    names = []
    for i, id_ in enumerate(idx[:50]):
        opinion = Opinion.get(Opinion.resource_id == citing[id_])
        names.append("{}: {}".format(i, opinion.cluster.case_name))
    return names


for case in nearest(108713):
    print(case)
