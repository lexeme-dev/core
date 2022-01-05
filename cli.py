import click

from algorithms import CaseSearch
from db.sqlalchemy import get_session, select
from db.sqlalchemy.models import Opinion
from utils.format import pretty_print_opinion


@click.group()
def cli():
    pass


@cli.command()
@click.argument('resource_id', type=int)
def lookup(resource_id: int):
    with get_session() as s:
        op = s.execute(select(Opinion).filter_by(resource_id=resource_id)).scalar()
    click.echo(pretty_print_opinion(op))


@cli.command()
@click.option('-n', '--num-cases', default=5, show_default=True, help='Maximum number of case results')
@click.argument('query', type=str)
def search(query: str, num_cases: int):
    search_results = CaseSearch.search_cases(query, max_cases=num_cases)
    output = f"{len(search_results)} result(s).\n\n"
    for op in search_results:
        output += f"{pretty_print_opinion(op)}\n\n"
    click.echo(output.strip())


if __name__ == '__main__':
    cli()
