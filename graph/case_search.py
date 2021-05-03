from functools import cache
from db.db_models import SearchableCase, Opinion, Cluster


class CaseSearch:
    @staticmethod
    @cache
    def search_cases(query, max_cases=25):
        return SearchableCase.select(SearchableCase) \
            .join(Opinion, on=(SearchableCase.opinion_id == Opinion.resource_id)) \
            .join(Cluster) \
            .where(SearchableCase.match(query)) \
            .order_by(Cluster.citation_count.desc()) \
            .limit(max_cases)
