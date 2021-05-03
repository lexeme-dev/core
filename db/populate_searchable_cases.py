from db_models import SearchableCase, Opinion, Cluster

if __name__ == '__main__':
    searchable_cases_dict = {}
    for op in Opinion.select().join(Cluster):
        if op.cluster.resource_id in searchable_cases_dict:
            continue
        searchable_cases_dict[op.cluster.resource_id] = \
            SearchableCase(
                case_name=op.cluster.case_name,
                reporter=op.cluster.reporter,
                year=op.cluster.year,
                opinion_id=op.resource_id,
                cluster_id=op.cluster.resource_id
            )
    searchable_cases = list(searchable_cases_dict.values())
    SearchableCase.bulk_create(searchable_cases, batch_size=1000)
