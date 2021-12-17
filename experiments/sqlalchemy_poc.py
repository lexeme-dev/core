from sqlalchemy import select

from db.sqlalchemy import get_session
from db.sqlalchemy.models import *

if __name__ == '__main__':
    with get_session() as session:
        res = session.execute(select(Citation.cited_opinion_id).filter_by(citing_opinion_id=117960)).scalars().all()
        print(res[0])
