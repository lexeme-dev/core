# We can no longer use SQLite's FTS5 as we move to PostgreSQL, so we're creating a new index and column here.
from deebee.peewee.models import deebee


def create_case_name_index():
    # I'm not adding parentheses around the year because my understanding is that to_tsvector would ignore them anyway.
    update_clusters_query = """
        ALTER TABLE cluster ADD COLUMN searchable_case_name tsvector;
        UPDATE cluster SET searchable_case_name = 
            to_tsvector('pg_catalog.english', case_name || ' ' || coalesce(reporter, '') || ' ' || year);
        CREATE INDEX searchable_case_name_idx ON cluster USING GIN (searchable_case_name);
    """
    print(update_clusters_query)
    deebee.execute_sql(update_clusters_query)
    pass


def create_case_index_trigger():
    trigger_query = """
    CREATE FUNCTION update_searchable_case_name_trigger() RETURNS trigger as $$
    begin
        new.searchable_case_name := 
            to_tsvector('pg_catalog.english', new.case_name || ' ' || coalesce(new.reporter, '') || ' ' || new.year);
        return new;
    end
    $$ LANGUAGE  plpgsql;
    
    CREATE TRIGGER update_searchable_case_name
    BEFORE INSERT OR UPDATE ON cluster
    FOR EACH ROW EXECUTE PROCEDURE update_searchable_case_name_trigger();
    """
    print(trigger_query)
    deebee.execute_sql(trigger_query)


if __name__ == '__main__':
    # deebee.execute_sql("DROP TRIGGER update_searchable_case_name ON cluster; DROP FUNCTION update_searchable_case_name_trigger;")
    create_case_name_index()
    create_case_index_trigger()
