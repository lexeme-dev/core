import regex


# noinspection RegExpUnnecessaryNonCapturingGroup,SpellCheckingInspection
class ParentheticalProcessor:
    __MODIFIABLE = r"(?:omissions?|quotations?|quotes?|headings?|(?:quotations? )?\Wmarks|ellips.s|cites?|citations?|emphas.s|italics?|footnotes?|alterations?|punctuation|modifications?|brackets?|bracketed material|formatting)"
    __MODIFABLE_TYPE = r"(?:internal|former|latter|first|second|last|some|further|certain|numbered|other|transcript)"
    __FULL_MODIFIABLE = f"(?:(?:{__MODIFABLE_TYPE} )?{__MODIFIABLE})"
    __QUOTE_MODIFICATION = r"(?:added|provided|removed|adopted|(?:in )?(?:the )original|omitted|included|deleted|eliminated|altered|modified|supplied|ours|mine|changed|(?:in|by) \S+|by \S+ court)"
    __DOCUMENT_TYPES = r"(?:opinion|continuance|order|op\.|decision|case|disposition|authority|authoritie|statement)"
    __OPINION_TYPES = r"(?:separate|supplemental|amended|majority|dissent|dissenting|concurrence|concurring|plurality|unpublished|revised|per curi.m|in.chambers|judgment|joint|principal|panel|unanimous|5-4)"
    __OPINION_TYPE_MODIFICATION = r"(?:in (?:the )?(?:judgment|result)s?(?: in part)?|in result|in part|dubitante|in relevant part|(?:from|with) .{1,25})"  # TIL: https://en.wikipedia.org/wiki/Dubitante
    __FULL_OPINION_DESCRIPTOR = (
        f"(?:{__OPINION_TYPES}(?: {__OPINION_TYPE_MODIFICATION})?)"
    )
    __REFERENTIAL = r"(?:quoting|citing|cited in|referencing)"
    __AGGREGATOR_TYPES = r"(?:collecting|reviewing|listing)"
    __HONORIFICS = r"(?:Mr.?|Mister)"
    __JUDGE_NAME = rf"(?:(?:.{{1,25}}J\.,?)|(?:{__HONORIFICS} Justice .{{1,25}})|the Court|(?:.{{1,25}}Circuit Justice),?)"

    _FUZZY_MODIFIABLE = rf"(?=.*{__MODIFIABLE}.*).{{1,75}}"

    __SURROUNDING_CHARS = r'[.!;," ]'

    PARENTHETICAL_REGEX_BLACKLIST_RULES = [
        r".n banc",  # en banc or in banc
        f"{__JUDGE_NAME}(?: {__FULL_OPINION_DESCRIPTOR})?(?: ?,?(?:and|,) {__FULL_OPINION_DESCRIPTOR})*",  # Scalia, J., dissenting; Roberts, C.J., concurring in the judgment
        f"(?:{__DOCUMENT_TYPES} )?{__FULL_OPINION_DESCRIPTOR}",  # concurring in result
        f"{__DOCUMENT_TYPES} of {__JUDGE_NAME}",  # opinion of Breyer, J.; opinion of Scalia and Alito, J.J.
        f"{__OPINION_TYPES}(?: {__DOCUMENT_TYPES})?(?: {__OPINION_TYPE_MODIFICATION})?",  # plurality opinion
        rf"({__DOCUMENT_TYPES} )?opinion.*",
        f"{__JUDGE_NAME}.{{1,50}}",
        r"dictum|dicta",
        r"standard of review",
        r"on rehearing|denying cert(iorari)?",
        r"simplified|cleaned up|as amended",
        r"same|similar|contra",
        r"(?:and )?cases cited therein",
        r"No. \d+.?\d+",  # No. 12-456
        r"f?n. \d+",  # n. 6
        f"{__DOCUMENT_TYPES} below",  # case below
        f"{__AGGREGATOR_TYPES} {__DOCUMENT_TYPES}s?",  # collecting cases, reviewing cases
        f"(?:{__OPINION_TYPES} )?table(?: {__DOCUMENT_TYPES})?",
        f"{__FULL_MODIFIABLE} {__QUOTE_MODIFICATION}",  # internal citations omitted
        f"{__FULL_MODIFIABLE} and {__FULL_MODIFIABLE} {__QUOTE_MODIFICATION}",
        f"{__FULL_MODIFIABLE} {__QUOTE_MODIFICATION}[;,] ?{__FULL_MODIFIABLE} {__QUOTE_MODIFICATION}",
        f"(?:{__MODIFABLE_TYPE} )?{__MODIFIABLE}, {__MODIFIABLE}, and {__MODIFIABLE} {__QUOTE_MODIFICATION}",
        f"{_FUZZY_MODIFIABLE}",
        f"{__REFERENTIAL} .*",  # citing Gonzales v. Raich, 123 U.S. 456 (2019). A tad over-inclusive but very helpful
        r".{1,10}\d{4}",  # 2nd Cir. 2019
        r".{1,25} I+",  # Gonzales II
        r".{1,10} (?:Circuit|Cir.)",  # Tenth Circuit, 5th Cir.
        r"here(?:in)?after .+",  # hereinafter, "Griffin II"
        r"\S*",  # Single-word parentheticals, e.g., 'TILA'
    ]

    __PREFIX = rf"^{__SURROUNDING_CHARS}*(?:"  # Begin string, optional whitespace, optional puncutation, begin capture group
    __SUFFIX = rf"){__SURROUNDING_CHARS}*$"  # Close capture group, optional punctuation, optional whitespace, end string

    PARENTHETICAL_BLACKLIST_REGEX = regex.compile(
        __PREFIX
        + r"|".join(map(lambda reg: f"(?:{reg})", PARENTHETICAL_REGEX_BLACKLIST_RULES))
        + __SUFFIX,
        regex.IGNORECASE,
    )

    @classmethod
    def is_descriptive(cls, text: str) -> bool:
        text = cls.prepare_text(text)
        return not regex.match(cls.PARENTHETICAL_BLACKLIST_REGEX, text)

    @classmethod
    def prepare_text(cls, text: str) -> str:
        text = regex.sub(r"\* ?\d+", " ", text)  # Remove star page numbers (e.g. *389)
        text = regex.sub(r" _{4,} ", " ", text)  # Remove weird "word ----- word" stuff
        text = regex.sub(r"\s+", " ", text)  # Remove excess whitespace
        text = regex.sub(r"[“”]", '"', text)  # Use ASCII quotes
        return text


if __name__ == "__main__":
    print(ParentheticalProcessor.PARENTHETICAL_BLACKLIST_REGEX.pattern)
