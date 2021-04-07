import requests
import re

CLURL = "https://www.courtlistener.com/api/rest/v3/search/?q={}&type=o"

def _hardstrip(s):
    """
    Strips all whitespace, punctuation, and lowers.
    To compare cites.
    """
    return re.sub(r"[^\w]", "", s).lower()

def cl_get(citation):
    """
    Searches a citation and returns its data from courtlistener.
    Must be a full bluebook cite (with reporter)
    """
    if not re.search("\d", citation):
        raise ValueError("Must be a full bluebook cite with reporter, volume, and page!")
    req = requests.get(CLURL.format(citation))
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

def oyez_get(approx_term, docket_number):
    approx_term = int(approx_term)
    for at in [approx_term + i for i in (-1, 0, 1, -2, 2)]:
        case = requests.get(f"http://api.oyez.org/cases/{at}/{docket_number}").json()
        if "name" in case:
            return case
    return None

def oyez_brief(*args):
    og = oyez_get(*args)
    if og:
        return {"facts": og["facts_of_the_case"], "question": og["question"], "conclusion": og["conclusion"]}
    else:
        return None

def casebrief(citation):
    cl = cl_get(citation)
    year = int(re.findall("\d{4}", citation)[-1])
    return oyez_brief(year, cl["docketNumber"])
