import re
from collections import defaultdict
from multiprocessing import Pool

from sqlalchemy.orm import Session

from db.sqlalchemy.models import (
    Opinion,
    Cluster,
    OpinionParenthetical,
    CitationContext,
    Court,
)
from db.sqlalchemy.helpers import get_session, ENGINE, get_db_url
from extraction.parenthetical_processor import ParentheticalProcessor
from ingress.helpers import JURISDICTIONS
from bs4 import BeautifulSoup
from sqlalchemy import select, create_engine
from utils.format import format_reporter
import eyecite
from eyecite.models import CaseCitation
from eyecite.tokenizers import Tokenizer, AhocorasickTokenizer, HyperscanTokenizer
from string import ascii_lowercase

from utils.io import get_full_path, HYPERSCAN_TMP_PATH
from utils.logger import Logger

STOP_WORDS = {
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
}
LETTERS = set(ascii_lowercase)


class OneTimeTokenizer(Tokenizer):
    """
    Wrap the CourtListener tokenizer to save tokenization results.
    """

    base_tokenizer: Tokenizer

    def __init__(self, base_tokenizer: Tokenizer):
        self.base_tokenizer = base_tokenizer
        self.words = []
        self.cit_toks = []

    def tokenize(self, text: str):
        if not self.words or self.cit_toks:
            # some of the static methods in AhocorasickTokenizer don't like children.
            self.words, self.cit_toks = self.base_tokenizer.tokenize(text)
        return self.words, self.cit_toks


class CitationContextScraper:
    eyecite_tokenizer: Tokenizer
    reporter_resource_dict: dict
    process_pool_size: int

    def __init__(self, process_pool_size=1):
        self.process_pool_size = process_pool_size

    def scrape_contexts(self):
        Logger.info("Constructing reporter to resource_id dict...")
        with get_session() as s:
            self.reporter_resource_dict = self.__get_reporter_resource_dict(s)
        try:
            Logger.info("Initializing Hyperscan tokenizer...")
            # noinspection PyPackageRequirements,PyUnresolvedReferences
            import hyperscan

            self.eyecite_tokenizer = HyperscanTokenizer(cache_dir=HYPERSCAN_TMP_PATH)
        except:
            Logger.info("Failed to initialize hyperscan, using Ahocorasick...")
            self.eyecite_tokenizer = AhocorasickTokenizer()
        with Pool(self.process_pool_size) as p:
            p.map(self.populate_jurisdiction_db_context, JURISDICTIONS)

    def __populate_db_contexts_for_opinion(
        self,
        session: Session,
        opinion: Opinion,
        reporter_resource_dict: dict,
        context_slice=slice(-128, 128),
    ) -> None:
        unstructured_html = opinion.html_text
        if not unstructured_html:
            raise ValueError(f"No HTML for case {opinion.resource_id}")
        unstructured_text = BeautifulSoup(unstructured_html, features="lxml").text
        clean_text = unstructured_text.replace("U. S.", "U.S.")
        tokenizer = OneTimeTokenizer(self.eyecite_tokenizer)
        citations = list(eyecite.get_citations(clean_text, tokenizer=tokenizer))
        cited_resources = eyecite.resolve_citations(citations)
        for resource, citation_list in cited_resources.items():
            cited_opinion_res_id = reporter_resource_dict.get(
                format_reporter(
                    resource.citation.groups.get("volume"),
                    resource.citation.groups.get("reporter"),
                    resource.citation.groups.get("page"),
                )
            )
            if cited_opinion_res_id is None:
                continue
            for citation in citation_list:
                if not isinstance(citation, CaseCitation):
                    continue
                if (
                    citation.metadata.parenthetical is not None
                    and ParentheticalProcessor.is_descriptive(
                        citation.metadata.parenthetical
                    )
                ):
                    session.add(
                        OpinionParenthetical(
                            citing_opinion_id=opinion.resource_id,
                            cited_opinion_id=cited_opinion_res_id,
                            text=ParentheticalProcessor.prepare_text(
                                citation.metadata.parenthetical
                            ),
                        )
                    )
                start = max(0, citation.index + context_slice.start)
                stop = min(len(tokenizer.words), citation.index + context_slice.stop)
                session.add(
                    CitationContext(
                        citing_opinion_id=opinion.resource_id,
                        cited_opinion_id=cited_opinion_res_id,
                        text=" ".join(
                            [
                                s
                                for s in tokenizer.words[start:stop]
                                if isinstance(s, str)
                            ]
                        ),
                    )
                )

    def __get_reporter_resource_dict(self, session: Session):
        reporter_resource_dict = {}
        reporter_max_citation_count = defaultdict(lambda: -1)
        for reporter, resource_id, citation_count in session.execute(
            select(Cluster.reporter, Opinion.resource_id, Cluster.citation_count).join(
                Cluster
            )
        ).iterator:
            if reporter not in reporter_resource_dict:
                reporter_resource_dict[reporter] = resource_id
                reporter_max_citation_count[reporter] = citation_count
            else:
                if citation_count > reporter_max_citation_count[reporter]:
                    reporter_resource_dict[reporter] = resource_id
                    reporter_max_citation_count[reporter] = citation_count
        return reporter_resource_dict

    def __batched_opinion_iterator(self, session: Session, jur: Court, batch_size=1000):
        page_no = 0
        while (
            opinions := session.execute(
                select(Opinion)
                .join(Cluster)
                .filter(Cluster.court == jur)
                .limit(batch_size)
                .offset(page_no * batch_size)
            )
            .scalars()
            .all()
        ):
            for op in opinions:
                yield op
            page_no += 1

    def populate_jurisdiction_db_context(self, jur: Court):
        s = Session(create_engine(get_db_url()))
        for i, op in enumerate(self.__batched_opinion_iterator(s, jur)):
            try:
                self.__populate_db_contexts_for_opinion(
                    s, op, self.reporter_resource_dict
                )
            except Exception as e:
                Logger.error(f"Failed {op.resource_id} with {e}!")
                continue
            if i > 0 and i % 1000 == 0:
                s.commit()
                if i % 10_000 == 0:
                    Logger.info(f"Completed {i} opinions for jurisdiction {jur}...")
        s.commit()


if __name__ == "__main__":
    CitationContextScraper(process_pool_size=4).scrape_contexts()
