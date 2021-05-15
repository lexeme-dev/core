from functools import cache
from db.db_models import Opinion, Cluster
from string import whitespace


class CaseSearch:
    @staticmethod
    @cache
    def search_cases(query, max_cases=25):
        query = CaseSearch.prepare_query(query)
        return (Opinion.select()
                .join(Cluster)
                .where(Cluster.searchable_case_name.match(query))
                .order_by(Cluster.citation_count.desc())
                .limit(max_cases))

    @staticmethod
    def prepare_query(query: str):
        """For now, just makes the query conform to tsquery syntax and adds prefix matching to last word."""
        if len(query.replace(' ', '')) == 0:
            return ''
        if query[-1] not in whitespace:
            query += ':*'  # Prefix match the last word
        query = "&".join(query.split())
        return query
