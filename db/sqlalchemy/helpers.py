import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def get_db_url() -> str:
    load_dotenv()
    if os.getenv("REMOTE_DB"):
        db_host, db_name, db_username, db_password, db_port = (os.getenv('REMOTE_DB_HOST'), os.getenv('REMOTE_DB_NAME'),
                                                               os.getenv('REMOTE_DB_USERNAME'),
                                                               os.getenv('REMOTE_DB_PASSWORD'),
                                                               os.getenv('REMOTE_DB_PORT'))
    else:
        db_host, db_name, db_username, db_password, db_port = (os.getenv('DB_HOST'), os.getenv('DB_NAME'),
                                                               os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'),
                                                               os.getenv('DB_PORT'))
    return f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"


ENGINE = create_engine(get_db_url())


# NOTE: Use sessions with a "with" block to ensure the session gets closed when done
def get_session() -> Session:
    return Session(ENGINE)
