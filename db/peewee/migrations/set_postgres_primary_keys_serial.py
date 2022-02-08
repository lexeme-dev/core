# For some god-forsaken reason, when I migrated the database it didn't set the id columns as serial, so
# now we're just gonna do it manually :/
from db.peewee.models import db


def set_primary_keys_to_serial():
    tables = ["cluster", "similarity", "opinion", "citation", "clustercitation"]
    for table_name in tables:
        serial_query = f"""
        CREATE SEQUENCE {table_name}_seq;
        ALTER TABLE {table_name} ALTER id SET DEFAULT nextval('{table_name}_seq');
        SELECT setval('{table_name}_seq', (SELECT max(id) from {table_name}) + 1);
        """
        db.execute_sql(serial_query)


if __name__ == "__main__":
    set_primary_keys_to_serial()
