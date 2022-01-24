from typing import Iterable, List, cast
from db.sqlalchemy.models import Opinion, Cluster, OpinionParenthetical, CitationContext
from sqlalchemy import select
from utils.format import format_reporter
import eyecite
from eyecite.models import (Resource as EyeciteResource, CitationBase, CaseCitation)
from eyecite.tokenizers import Tokenizer, AhocorasickTokenizer
import re
from string import punctuation
from string import ascii_lowercase

STOP_WORDS = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves', ' ', 'court', "court's"])
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


def populate_db_contexts(session, opinion_id: int):
    unstructured_html = session.query(Opinion).filter(Opinion.resource_id==opinion_id).first().html_text
    clean_text = unstructured_html.replace("U. S.", "U.S.")
    tokenizer = OneTimeTokenizer()
    citations = list(eyecite.get_citations(clean_text, tokenizer=tokenizer))
    cited_resources = eyecite.resolve_citations(citations)
    reporter_resource_dict = {format_reporter(res.citation.groups.get('volume'), res.citation.groups.get('reporter'), res.citation.groups.get('page')): res
                              for res in cited_resources}
    stmt = select(Opinion).join(Cluster).where(Cluster.reporter.in_(reporter_resource_dict.keys()))
    opinions = []
    breakpoint()
    for opinon in session.execute(stmt).iterator:
        parentheticals = []
        contexts = []
        for citation in cited_resources[reporter_resource_dict[opinion.cluster.reporter]]:
            if isinstance(citation, CaseCitation):
                if citation.metadata.parenthetical is not None:
                    opinion.parentheticals.append(OpinionParenthetical(citing_opinion_id=opinion_id,
                                                                       cited_opinion_id=citation.metadata.resource_id,
                                                                       text=citation.metadata.parenthetical))
                start = max(0, citation.index + context_slice.start)
                stop = min(len(self.tokenizer.words), citation.index + context_slice.stop)
                # contexts.append(list(self.clean_contexts(self.tokenizer.words[start:stop])))
                opinion.contexts.append(OpinionContext(citing_opinion_id=opinion_id,
                                                       cited_opinion_id=citation.metadata.resource_id,
                                                       text=" ".join(self.tokenizer.words[start:stop])))
        opinions.append(opinion)
    return opinions
