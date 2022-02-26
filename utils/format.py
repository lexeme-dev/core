from sqlalchemy import desc

from db.peewee.models import Opinion
from db.sqlalchemy import get_session, select
from db.sqlalchemy.models import OpinionParenthetical


def format_reporter(volume, reporter, page):
    return f"{volume} {reporter} {page}"


def pretty_print_opinion(opinion: Opinion) -> str:
    output = ""
    output += f"{opinion.cluster.case_name}, {opinion.cluster.reporter} ({opinion.cluster.year})\n"
    output += f"CourtListener URI: {opinion.opinion_uri}\n"
    output += f"Court: {opinion.cluster.court}"
    # Mixing SQLAlchemy and peewee = not good, but not much choice at the moment
    with get_session() as s:
        top_parenthetical = s.execute(
            select(OpinionParenthetical)
            .filter_by(cited_opinion_id=opinion.resource_id)
            .order_by(desc(OpinionParenthetical.score))
            .limit(1)
        ).scalar()
    if top_parenthetical:
        output += f"\nTop Parenthetical: {top_parenthetical.text}"
    return output
