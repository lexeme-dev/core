from typing import Optional

import click

from algorithms import CaseSearch
from api import app
from db.sqlalchemy import get_session, select
from db.sqlalchemy.models import Opinion
from ingress.cl_file_downloader import ClFileDownloader
from ingress.db_updater import DbUpdater
from ingress.helpers import JURISDICTIONS
from utils.format import pretty_print_opinion


@click.group()
def cli():
    pass


@cli.group(help='Commands to manage the API server')
def server():
    pass


@server.command(name='run', help='Run the Flask API server')
@click.option('--host', '-h', help='The interface to bind to')
@click.option('--port', '-p', type=int, help='The port to bind to')
@click.option('--debug/--no-debug', default=False, show_default=True,
              help='Whether to run the Flask server in debug mode')
def server_run(debug: bool, host: Optional[str], port: Optional[int]):
    app.run(host=host, port=port, debug=debug)


@cli.group(help='Commands to download data and populate the database')
def data():
    pass


@data.command(name='download', help='Download and extract CourtListener jurisdiction data')
@click.option('-j', '--jurisdictions', type=str, required=True,
              help='Comma-separated list of jurisdictions to download data for. "all" downloads data for all known jurisdictions.')
def data_download(jurisdictions: str):
    jurisdictions_arr = list(
        filter(None, [j for j in jurisdictions.split(',')])) if jurisdictions != 'all' else JURISDICTIONS
    ClFileDownloader(jurisdictions=jurisdictions_arr).download()


@data.command(name='update', help='Update database from downloaded CourtListener data')
@click.option('-j', '--jurisdictions', type=str, required=True,
              help='Comma-separated list of jurisdictions to update db for. "all" updates all known jurisdictions.')
@click.option('--include-text-for', type=str,
              help='Comma-separated list of jurisdictions to update opinion text for. "all" updates text for all known jurisdictions.')
@click.option('--force-update/--no-force-update', default=False, show_default=True,
              help='Updates all database records even if JSON hashes match (indicating no changes since last update).')
def data_update(jurisdictions: str, include_text_for: str, force_update: bool):
    jurisdictions_arr = list(
        filter(None, [j for j in jurisdictions.split(',')])) if jurisdictions != 'all' else JURISDICTIONS
    include_text_for_arr = list(
        filter(None, [j for j in include_text_for.split(',')])) if include_text_for != 'all' else JURISDICTIONS
    click.echo(f"Beginning db update for jurisdictions: {jurisdictions_arr}...")
    click.echo(f"Including opinion text for jurisdictions: {include_text_for_arr}...")
    DbUpdater(jurisdictions=jurisdictions_arr, include_text_for=include_text_for_arr,
              force_update=force_update).update_from_cl_data()


@cli.group(help='Utilities to search and look up cases')
def case():
    pass


@case.command(name='lookup', help='Look up case info by opinion resource ID')
@click.argument('resource_id', type=int)
def case_lookup(resource_id: int):
    with get_session() as s:
        op = s.execute(select(Opinion).filter_by(resource_id=resource_id)).scalar()
        if not op:
            raise ValueError(f"Resource id {resource_id} not located in current db.")
        click.echo(pretty_print_opinion(op))

@case.command(name='search', help='Search cases by name')
@click.option('-n', '--num-cases', default=5, show_default=True, help='Maximum number of case results')
@click.argument('query', type=str)
def case_search(query: str, num_cases: int):
    search_results = CaseSearch.search_cases(query, max_cases=num_cases)
    output = f"{len(search_results)} result(s).\n\n"
    for op in search_results:
        output += f"{pretty_print_opinion(op)}\n\n"
    click.echo(output.strip())
