from typing import Iterable, List
from db.db_models import Opinion


def opinion_ids_to_names(opinion_ids: Iterable[str]) -> List[str]:
    op_names = []
    for op_id in opinion_ids:
        if (op_model := Opinion.select().where(Opinion.resource_id == op_id).first()) is not None:
            op_names.append(op_model.cluster.case_name)
        else:
            op_names.append("Unknown")
    return op_names
