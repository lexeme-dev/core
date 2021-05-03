from functools import cache
from db.db_models import SearchableCase, Opinion, Cluster


class CaseSearch:
    @staticmethod
    @cache
    def search_cases(query, max_cases=25):
        return Opinion.select() \
            .join(SearchableCase, on=(SearchableCase.opinion_id == Opinion.resource_id)) \
            .switch(Opinion).join(Cluster) \
            .where(SearchableCase.match(query)) \
            .order_by(Cluster.citation_count.desc()) \
            .limit(max_cases)
