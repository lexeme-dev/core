from typing import Iterable, List, cast, NamedTuple
from db.db_models import Opinion, Cluster
from helpers import format_reporter
import eyecite
from eyecite.models import Resource as EyeciteResource


class CitationExtractor:
    unstructured_text: str

    def __init__(self, unstructured_text: str):
        self.unstructured_text = unstructured_text

    def get_citations(self) -> List[EyeciteResource]:
        return cast(List[EyeciteResource],
                    list(eyecite.resolve_citations(eyecite.get_citations(self.unstructured_text)).keys())
                    )  # :/ Yikes. The cast is to make type hints cooperate (eyecite's typing is incorrect).

    def get_opinion_citations(self) -> Iterable[Opinion]:
        """
        Returns Opinion objects (if found) for the cases cited in the given text. This method is *very* imperfect
        because it only checks the reporter, which may be missing, duplicate, or of the wrong kind.

        TODO: Make requisite improvements to our data and this method to fix.

        :return: An iterable of db_models.Opinion objects corresponding to cases cited by the given unstructured text.
        """
        reporters_of_cited_cases = [format_reporter(volume=res.citation.volume, reporter=res.citation.reporter,
                                                    page=res.citation.page) for res in self.get_citations()]
        return Opinion.select().join(Cluster).where(Cluster.reporter << reporters_of_cited_cases)
