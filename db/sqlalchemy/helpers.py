from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from helpers import get_db_url

ENGINE = create_engine(get_db_url())


# NOTE: Use sessions with a "with" block to ensure the session gets closed when done
def get_session() -> Session:
    return Session(ENGINE)
