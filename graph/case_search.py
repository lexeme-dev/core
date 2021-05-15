from functools import cache
from db.db_models import Opinion, Cluster


class CaseSearch:
    @staticmethod
    @cache
    def search_cases(query, max_cases=25):
        return (Opinion.select()
                .join(Cluster)
                .where(Cluster.searchable_case_name.match(query))
                .order_by(Cluster.citation_count.desc())
                .limit(max_cases))
