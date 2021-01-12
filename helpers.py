from db_models import db, Opinion, Cluster


def get_names_for_id_collection(collection):
    names = []
    for op_id in collection:
        try:
            name = Opinion.get(Opinion.resource_id == op_id).cluster.case_name
            names.append(name)
        except:
            names.append("Unknown")
    return names
