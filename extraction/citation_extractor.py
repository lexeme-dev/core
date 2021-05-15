from typing import Iterable, List, cast
from db.db_models import Opinion, Cluster
from helpers import format_reporter
import eyecite
from eyecite.models import (Resource as EyeciteResource, CitationBase, CaseCitation)


class CitationExtractor:
    unstructured_text: str

    def __init__(self, unstructured_text: str):
        self.unstructured_text = unstructured_text

    def get_citations(self) -> List[CitationBase]:
        return list(eyecite.get_citations(self.unstructured_text))

    def get_extracted_citations(self) -> List[Opinion]:
        cited_resources = eyecite.resolve_citations(self.get_citations())
        reporter_resource_dict = {format_reporter(res.citation.groups['volume'], res.citation.groups['reporter'], res.citation.groups['page']): res
                                  for res in cited_resources}
        opinions = self.get_opinion_citations(cited_resources)
        extracted_citations = []
        for opinion in opinions:
            parentheticals = []
            for citation in cited_resources[reporter_resource_dict[opinion.cluster.reporter]]:
                if isinstance(citation, CaseCitation) \
                        and citation.metadata.parenthetical is not None:
                    parentheticals.append(citation.metadata.parenthetical)
            opinion.parentheticals = parentheticals
            extracted_citations.append(opinion)
        return extracted_citations

    def get_opinion_citations(self, cited_resources=None) -> Iterable[Opinion]:
        """
        Returns Opinion objects (if found) for the cases cited in the given text. This method is *very* imperfect
        because it only checks the reporter, which may be missing, duplicate, or of the wrong kind.

        TODO: Make requisite improvements to our data and this method to fix.

        :return: An iterable of db_models.Opinion objects corresponding to cases cited by the given unstructured text.
        """
        if cited_resources is None:
            cited_resources = eyecite.resolve_citations(self.get_citations())
        unique_resources = cast(List[EyeciteResource], list(cited_resources.keys()))
        reporters_of_cited_cases = {format_reporter(volume=res.citation.groups['volume'], reporter=res.citation.groups['reporter'],
                                                    page=res.citation.groups['page']): i for i, res in
                                    enumerate(unique_resources)}
        return sorted(Opinion.select().join(Cluster).where(Cluster.reporter << list(reporters_of_cited_cases.keys())),
                      key=lambda op: reporters_of_cited_cases[op.cluster.reporter])
