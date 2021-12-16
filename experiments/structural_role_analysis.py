import csv
from dataclasses import dataclass
from typing import Dict, List
from helpers import get_full_path
from db.models import Citation

STRUCTURAL_ROLE_FILE_PATH = 'data/structural_roles.csv'

RoleDict = Dict[str, List[str]]


@dataclass
class RoleSummary:
    role_id: str
    average_in_degree: float
    average_out_degree: float
    num_nodes: float


def role_dict_from_file() -> RoleDict:
    role_dict = {}  # Key: role identifier, Value: list of resource IDs with key's role
    with open(get_full_path(STRUCTURAL_ROLE_FILE_PATH), 'r') as role_file:
        role_csv_reader = csv.reader(role_file)
        next(role_csv_reader)  # First row is header
        for resource_id, role_id in role_csv_reader:
            if role_id not in role_dict:
                role_dict[role_id] = []
            role_dict[role_id].append(resource_id)
    return role_dict


def get_role_summaries(role_dict: RoleDict) -> List[RoleSummary]:
    role_summaries = []
    for role_id, resource_ids in role_dict.items():
        num_nodes = len(resource_ids)
        average_in_degree = Citation.select().where(Citation.cited_opinion_id << resource_ids).count() / len(
            resource_ids)
        average_out_degree = Citation.select().where(Citation.citing_opinion_id << resource_ids).count() / len(
            resource_ids)
        role_summaries.append(
            RoleSummary(
                role_id=role_id,
                num_nodes=num_nodes,
                average_in_degree=average_in_degree,
                average_out_degree=average_out_degree
            )
        )
    return role_summaries


def formatted_role_summary(role_summary: RoleSummary) -> str:
    return f"""
    ROLE: {role_summary.role_id}
      SIZE: {role_summary.num_nodes}
      AVERAGE OUT DEGREE: {round(role_summary.average_out_degree, 2)}
      AVERAGE IN DEGREE: {round(role_summary.average_in_degree, 2)}
    """.strip()


if __name__ == '__main__':
    role_dict = role_dict_from_file()
    role_summaries = get_role_summaries(role_dict)
    for summary in role_summaries:
        print(formatted_role_summary(summary))
