from peewee import Expression


def ts_match(vector, query):
    return Expression(vector, '@@', query)
