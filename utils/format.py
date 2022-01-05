from db.sqlalchemy.models import Opinion


def format_reporter(volume, reporter, page):
    return f"{volume} {reporter} {page}"


def pretty_print_opinion(opinion: Opinion) -> str:
    output = ""
    output += f"{opinion.cluster.case_name}, {opinion.cluster.reporter} ({opinion.cluster.year})\n"
    output += f"CourtListener URI: {opinion.opinion_uri}\n"
    output += f"Court: {opinion.cluster.court}"
    return output
