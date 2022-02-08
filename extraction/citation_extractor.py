from typing import Iterable, List, cast
from db.sqlalchemy.models import Opinion, Cluster
from sqlalchemy import select
from utils.format import format_reporter
import eyecite
from eyecite.models import Resource as EyeciteResource, CitationBase, CaseCitation
from eyecite.tokenizers import Tokenizer, AhocorasickTokenizer
import re
from string import punctuation
from string import ascii_lowercase

STOP_WORDS = set(
    [
        "a",
        "about",
        "above",
        "after",
        "again",
        "against",
        "all",
        "am",
        "an",
        "and",
        "any",
        "are",
        "aren't",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can't",
        "cannot",
        "could",
        "couldn't",
        "did",
        "didn't",
        "do",
        "does",
        "doesn't",
        "doing",
        "don't",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "hadn't",
        "has",
        "hasn't",
        "have",
        "haven't",
        "having",
        "he",
        "he'd",
        "he'll",
        "he's",
        "her",
        "here",
        "here's",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "how's",
        "i",
        "i'd",
        "i'll",
        "i'm",
        "i've",
        "if",
        "in",
        "into",
        "is",
        "isn't",
        "it",
        "it's",
        "its",
        "itself",
        "let's",
        "me",
        "more",
        "most",
        "mustn't",
        "my",
        "myself",
        "no",
        "nor",
        "not",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "ought",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "same",
        "shan't",
        "she",
        "she'd",
        "she'll",
        "she's",
        "should",
        "shouldn't",
        "so",
        "some",
        "such",
        "than",
        "that",
        "that's",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "there's",
        "these",
        "they",
        "they'd",
        "they'll",
        "they're",
        "they've",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "very",
        "was",
        "wasn't",
        "we",
        "we'd",
        "we'll",
        "we're",
        "we've",
        "were",
        "weren't",
        "what",
        "what's",
        "when",
        "when's",
        "where",
        "where's",
        "which",
        "while",
        "who",
        "who's",
        "whom",
        "why",
        "why's",
        "with",
        "won't",
        "would",
        "wouldn't",
        "you",
        "you'd",
        "you'll",
        "you're",
        "you've",
        "your",
        "yours",
        "yourself",
        "yourselves",
        " ",
        "court",
        "court's",
    ]
)
LETTERS = set(ascii_lowercase)


class OneTimeTokenizer(Tokenizer):
    """
    Wrap the CourtListener tokenizer to save tokenization results.
    """

    def __init__(self):
        self.words = []
        self.cit_toks = []

    def tokenize(self, text: str):
        if not self.words or self.cit_toks:
            # some of the static methods in AhocorasickTokenizer don't like children.
            self.words, self.cit_toks = AhocorasickTokenizer().tokenize(text)
        return self.words, self.cit_toks


class CitationExtractor:
    unstructured_text: str

    def __init__(self, unstructured_text: str, sqlalchemy_session=None):
        # Allows eyecite to detect reporter citations when a whitespace exists between the letters of the abbreviation
        cleaned_text = unstructured_text.replace("U. S. ", "U.S. ")
        self.unstructured_text = cleaned_text
        self.sqlalchemy_session = sqlalchemy_session

    def get_citations(self) -> List[CitationBase]:
        self.tokenizer = OneTimeTokenizer()
        return list(
            eyecite.get_citations(self.unstructured_text, tokenizer=self.tokenizer)
        )

    def clean_contexts(self, contexts):
        """Return True if context is significant, else False"""
        for c in contexts:
            if not isinstance(c, str):
                continue
            c = c.strip(punctuation).lower()
            if len(c) < 3:
                continue
            if c in STOP_WORDS or (c[0] not in LETTERS):
                continue
            yield c

    def get_extracted_citations(
        self, context_slice: slice = slice(-128, 128)
    ) -> List[Opinion]:
        cited_resources = eyecite.resolve_citations(self.get_citations())
        reporter_resource_dict = {
            format_reporter(
                res.citation.groups.get("volume"),
                res.citation.groups.get("reporter"),
                res.citation.groups.get("page"),
            ): res
            for res in cited_resources
        }
        opinions = self.get_opinion_citations(cited_resources)
        extracted_citations = []
        for opinion in opinions:
            parentheticals = []
            contexts = []
            for citation in cited_resources[
                reporter_resource_dict[opinion.cluster.reporter]
            ]:
                if isinstance(citation, CaseCitation):
                    if citation.metadata.parenthetical is not None:
                        parentheticals.append(citation.metadata.parenthetical)
                    start = max(0, citation.index + context_slice.start)
                    stop = min(
                        len(self.tokenizer.words), citation.index + context_slice.stop
                    )
                    contexts.append(
                        list(self.clean_contexts(self.tokenizer.words[start:stop]))
                    )
            opinion.parentheticals.append(parentheticals)
            opinion.contexts(contexts)
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
        reporters_of_cited_cases = {
            format_reporter(
                volume=res.citation.groups.get("volume"),
                reporter=res.citation.groups.get("reporter"),
                page=res.citation.groups.get("page"),
            ): i
            for i, res in enumerate(unique_resources)
        }
        stmt = (
            select(Opinion)
            .join(Cluster)
            .where(Cluster.reporter.in_(reporters_of_cited_cases.keys()))
        )
        return sorted(
            self.sqlalchemy_session.execute(stmt).iterator,
            key=lambda op: reporters_of_cited_cases[op.cluster.reporter],
        )
