from collections import namedtuple
from itertools import chain
import requests
import re

CLSEARCH = "https://www.courtlistener.com/api/rest/v3/search/?q={}&type=o"
CLID = "https://www.courtlistener.com/api/rest/v3/opinions/{}"


def _hardstrip(s):
    """
    Strips all whitespace, punctuation, and lowers.
    To compare cites.
    """
    return re.sub(r"[^\w]", "", s).lower()

def _cl_get_from_resource_id(rid: int):
    req = requests.get(CLID.format(rid))
    if not req:
        raise ValueError(f"Could not find resource id {rid} in CourtListener!")
    case_init = req.json()
    cluster = requests.get(case_init["cluster"]).json()
    docket = requests.get(cluster["docket"]).json()
    case = {}
    # this has to be done bc of the way python's default cat operators work
    for k, v in chain(case_init.items(), cluster.items(), docket.items()):
        if not (k in case and case[k]):
            case[k] = v
    return case

def _cl_get_from_cite(citation: str):
    """
    Searches a citation and returns its data from courtlistener.
    Must be a full bluebook cite (with reporter)
    """
    if not re.search("\d", citation):
        raise ValueError("Must be a full bluebook cite with reporter, volume, and page!")
    req = requests.get(CLSEARCH.format(citation))
    if not req:
        raise ValueError("Could not find citation in CourtListener!")
    values = req.json()
    case = values["results"]
    try:
        case = case[0]
    except IndexError:
        raise ValueError("{} not found in CourtListener!".format(citation))
    cites = case["citation"]
    if not any([_hardstrip(c) in _hardstrip(citation) for c in cites]):
        raise ValueError("{} not found in CourtListener! Closest match was {}".format(citation, case["caseName"]))
    return case


def _oyez_get(approx_term: int, docket_number: str):
    approx_term = int(approx_term)
    for at in [approx_term + i for i in (-1, 0, 1, -2, 2)]:
        case = requests.get(f"http://api.oyez.org/cases/{at}/{docket_number}").json()
        if "name" in case:
            return case
    return None

OyezBrief = namedtuple("OyezBrief", ["facts", "question", "conclusion"])
def _oyez_brief(approx_term: int, docket_number: str) -> OyezBrief:
    og = _oyez_get(approx_term, docket_number)
    if og:
        return OyezBrief(og["facts_of_the_case"], og["question"], og["conclusion"])
    else:
        return None


def from_cite(citation: str) -> OyezBrief:
    cl = _cl_get_from_cite(citation)
    year = int(re.findall("\d{4}", citation)[-1])
    try:
        return _oyez_brief(year, cl["docketNumber"])
    except KeyError:
        return None

def from_resource_id(rid: int) -> OyezBrief:
    cl = _cl_get_from_resource_id(rid)
    try:
        year = int(re.findall("\d{4}", cl["date_filed"])[-1])
        return _oyez_brief(year, cl["docket_number"])
    except KeyError:
        return None
