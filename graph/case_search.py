from functools import cache
from db.db_models import SearchableCase, Opinion, Cluster


class CaseSearch:
    @staticmethod
    @cache
    def search_cases(query, max_cases=25):
        return (case.opinion for case in
                SearchableCase.search(query)
                    .join(Opinion, on=Opinion.resource_id == SearchableCase.opinion_id)
                    .join(Cluster)
                    .select(Opinion)
                    .order_by(Cluster.citation_count.desc())
                    .limit(max_cases))
