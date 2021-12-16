from peewee import fn
from db.peewee.helpers import ts_match
from db.peewee.models import Opinion, Cluster
from string import whitespace


class CaseSearch:
    @staticmethod
    def search_cases(query, max_cases=25):
        search_text = CaseSearch.prepare_query(query)
        return (Opinion.select(Opinion,
                               fn.ts_headline(Cluster.case_display_name(), fn.to_tsquery(search_text)).alias('headline'))
                .join(Cluster)
                .where(ts_match(Cluster.searchable_case_name, fn.to_tsquery(search_text)))
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
