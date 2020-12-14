from db_models import db, Citation, Opinion
import numpy as np

MAX_DEPTH = 122  # To normalize lowest edge weight to 1


def construct_mat():
    db.connect()
    citations = np.array([ \
            (c.citing_opinion, c.cited_opinion, c.depth) \
            for c in Citation.select()])
    db.close()
    # idk if this is the most efficient way to do this
    citing = np.unique(citations.T[0])
    cited = np.unique(citations.T[1])
    mat = np.zeros((len(citing), len(cited)))
    for ing, ed, depth in citations:
        mat[np.where(citing==ing)[0][0], np.where(cited==ed)[0][0]] += depth
    return (mat, citing, cited)

mat, citing, cited = construct_mat()

def nearest(resource_id):
    global citing
    vec = mat[np.where(citing==resource_id)[0][0]]
    vmat = np.array((vec,)*len(citing))
    diff = vmat - mat
    dist = np.linalg.norm(diff, axis=1)
    idx = np.argsort(dist)
    names = []
    for i, id_ in enumerate(idx[:50]):
        opinion = Opinion.get(Opinion.resource_id == citing[id_])
        names.append("{}: {}".format(i, opinion.cluster.case_name))
    return names
