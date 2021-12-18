from alembic_utils.pg_extension import PGExtension
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

# NOTE: When adding any new entities, remember to add it to the PG_ENTITY_LIST at the bottom of this file.

pg_trgm_extension = PGExtension(
    schema='public',
    signature='pg_trgm'
)

update_searchable_case_name_func = PGFunction(
    schema='public',
    signature='update_searchable_case_name_trigger()',
    definition="""
      RETURNS trigger
      LANGUAGE plpgsql
      AS $$
      begin
          new.searchable_case_name := 
              to_tsvector('pg_catalog.english', new.case_name || ' ' || coalesce(new.reporter, '') || ' ' || new.year);
          return new;
      end
      $$;
  """
)

update_searchable_case_name_trigger = PGTrigger(
    schema='public',
    signature='update_searchable_case_name',
    on_entity='public.cluster',
    definition="""
      BEFORE INSERT OR UPDATE ON public.cluster
      FOR EACH ROW EXECUTE PROCEDURE public.update_searchable_case_name_trigger()
  """
)

PG_ENTITY_LIST = [pg_trgm_extension, update_searchable_case_name_func, update_searchable_case_name_trigger]
