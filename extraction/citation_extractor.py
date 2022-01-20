from typing import Iterable, List, cast
from db.peewee.models import Opinion, Cluster
from utils.format import format_reporter
import eyecite
from eyecite.models import (Resource as EyeciteResource, CitationBase, CaseCitation)
from eyecite.tokenizers import Tokenizer, AhocorasickTokenizer

class OneTimeTokenizer(AhocorasickTokenizer):
    """
    Wrap the CourtListener tokenizer to save tokenization results.
    """
    def __init__(self):
        self.words = []
        self.cit_toks = []

    def tokenize(self, text: str):
        if not self.words or self.cit_toks:
            self.words, self.cit_toks = super().tokenize(text)
        return self.words, self.cit_toks

class CitationExtractor:
    unstructured_text: str

    def __init__(self, unstructured_text: str):
        # Allows eyecite to detect reporter citations when a whitespace exists between the letters of the abbreviation
        cleaned_text = unstructured_text.replace("U. S. ", "U.S. ")
        self.unstructured_text = cleaned_text

    def get_citations(self) -> List[CitationBase]:
        self.tokenizer = OneTimeTokenizer()
        return list(eyecite.get_citations(self.unstructured_text, tokenizer=self.tokenizer))

    def get_extracted_citations(self, context_slice: slice) -> List[Opinion]:
        cited_resources = eyecite.resolve_citations(self.get_citations())
        reporter_resource_dict = {format_reporter(res.citation.groups.get('volume'), res.citation.groups.get('reporter'), res.citation.groups.get('page')): res
                                  for res in cited_resources}
        opinions = self.get_opinion_citations(cited_resources)
        extracted_citations = []
        for opinion in opinions:
            parentheticals = []
            contexts = []
            for citation in cited_resources[reporter_resource_dict[opinion.cluster.reporter]]:
                if isinstance(citation, CaseCitation):
                    if citation.metadata.parenthetical is not None:
                        parentheticals.append(citation.metadata.parenthetical)
                    start = max(0, citation.index - context_slice.start)
                    stop = min(len(self.tokenizer.words), citation.index + context_slice.stop)
                    contexts.append([w for w in self.tokenizer.words[start:stop] if isinstance(w, str)])
            opinion.ingest_parentheticals(parentheticals)
            opinion.ingest_contexts(contexts)
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
        reporters_of_cited_cases = {format_reporter(volume=res.citation.groups.get('volume'), reporter=res.citation.groups.get('reporter'),
                                                    page=res.citation.groups.get('page')): i for i, res in
                                    enumerate(unique_resources)}
        return sorted(Opinion.select().join(Cluster).where(Cluster.reporter << list(reporters_of_cited_cases.keys())),
                      key=lambda op: reporters_of_cited_cases[op.cluster.reporter])
