import re
from collections import defaultdict
from db.sqlalchemy.models import Opinion, Cluster, OpinionParenthetical, CitationContext, Court
from bs4 import BeautifulSoup
from sqlalchemy import select
from utils.format import format_reporter
import eyecite
from eyecite.models import CaseCitation
from eyecite.tokenizers import Tokenizer, AhocorasickTokenizer
from string import ascii_lowercase

from utils.logger import Logger

STOP_WORDS = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't",
              'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't",
              'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down',
              'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't",
              'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself',
              'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's",
              'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of',
              'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
              'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than',
              'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these',
              'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under',
              'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't",
              'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why',
              "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your',
              'yours', 'yourself', 'yourselves', ' ', 'court', "court's"}
LETTERS = set(ascii_lowercase)
PARENTHETICAL_BLACKLIST_REGEX = re.compile(
    r"^\s*(?:(?:(?:(?:majority|concurring|dissenting|in chambers|for the Court)(?: (in part|in judgment|in judgment in part|in result)?)(?: and (?:(?:concurring|dissenting|in chambers|for the Court)(?: (in part|in judgment|in judgment in part|in result)?)?)?)?) opinion)|(?:(?:(?:majority|concurring|dissenting|in chambers|for the Court)(?: (in part|in judgment|in judgment in part|in result)?)(?: and (?:(?:concurring|dissenting|in chambers|for the Court)(?: (in part|in judgment|in judgment in part|in result))?)?)?)? ?opinion of \S+ (?:J.|C.\s*J.))|(?:(?:quoting|citing).*)|(?:per curiam)|(?:(?:plurality|majority|dissenting|concurring)(?: (?:opinion|statement))?)|(?:\S+,\s*(?:J.|C.\s*J.(?:, joined by .*,)?)(?:, (?:(?:concurring|dissenting|in chambers|for the Court)(?: (in part|in judgment|in judgment in part|in result|(?:from|with|respecting) ?denial of certiorari)?)?(?: and (?:(?:concurring|dissenting|in chambers|for the Court)(?: (in part|in(?: the)? judgment|in judgment in part|in result|(?:from|with|respecting) denial of certiorari))?)?)?))?)|(?:(?:some )?(?:internal )?(?:brackets?|footnotes?|alterations?|quotations?|quotation marks?|citations?|emphasis)(?: and (?:brackets?|footnotes?|alterations?|quotations?|quotation marks?|citations?|emphasis))? (?:added|omitted|deleted|in original|altered|modified))|(?:same|similar)|(?:slip op.* \d*)|denying certiorari|\w+(?: I{1,3})?|opinion in chambers|opinion of .*)\s*$")


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


def populate_db_contexts(session, opinion: Opinion, reporter_to_resource_id: dict, context_slice=slice(-128, 128)) => None:
    unstructured_html = opinion.html_text
    if not unstructured_html:
        raise ValueError(f"No HTML for case {opinion.resource_id}")
    unstructured_text = BeautifulSoup(unstructured_html, features="lxml").text
    clean_text = unstructured_text.replace("U. S.", "U.S.")
    tokenizer = OneTimeTokenizer()
    citations = list(eyecite.get_citations(clean_text, tokenizer=tokenizer))
    cited_resources = eyecite.resolve_citations(citations)
    reporter_resource_dict = {: res
                              for res in cited_resources}
    for resource, citation_list in cited_resources:
        for citation in citation_list:
            if not isinstance(citation, CaseCitation):
                continue
            cited_opinion_res_id = reporter_to_resource_id[
                format_reporter(res.citation.groups.get('volume'),
                                res.citation.groups.get('reporter'),
                                res.citation.groups.get('page'))]
            if citation.metadata.parenthetical is not None and not PARENTHETICAL_BLACKLIST_REGEX.match(
                    citation.metadata.parenthetical):
                session.add(OpinionParenthetical(citing_opinion_id=opinion.resource_id,
                            cited_opinion_id=cited_opinion_res_id,
                            text=citation.metadata.parenthetical))
            start = max(0, citation.index + context_slice.start)
            stop = min(len(tokenizer.words), citation.index + context_slice.stop)
            session.add(CitationContext(citing_opinion_id=opinion.resource_id,
                                        cited_opinion_id=cited_opinion_res_id,
                                        text="".join([s for s in tokenizer.words[start:stop] if isinstance(s, str)])))


def populate_all_db_contexts():
    from db.sqlalchemy.helpers import get_session
    s = get_session()
    reporter_resource_dict = get_reporter_resource_dict(s)
    for i, op in enumerate(s.execute(select(Opinion)).iterator):
        try:
            populate_db_contexts(s, op.resource_id, reporter_resource_dict)
        except Exception as e:
            Logger.error(f"Failed {op.resource_id} with {e}!")
            continue
        Logger.info(f"Completed {op.resource_id}")
        if i > 0 and i % 1000 == 0:
            s.commit()
    s.commit()


def get_reporter_resource_dict(s):
    reporter_resource_dict = {}
    reporter_max_citation_count = defaultdict(lambda: -1)
    for reporter, resource_id, citation_count in s.execute(
            select(Cluster.reporter, Opinion.resource_id, Cluster.citation_count).join(Cluster)).iterator:
        if reporter not in reporter_resource_dict:
            reporter_resource_dict[reporter] = resource_id
            reporter_max_citation_count[reporter] = citation_count
        else:
            if citation_count > reporter_max_citation_count[reporter]:
                reporter_resource_dict[reporter] = resource_id
                reporter_max_citation_count[reporter] = citation_count
    return reporter_resource_dict


if __name__ == '__main__':
    populate_all_db_contexts()
