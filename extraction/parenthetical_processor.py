import re


# noinspection RegExpUnnecessaryNonCapturingGroup,SpellCheckingInspection
class ParentheticalProcessor:
    __MODIFIABLE = r'(?:quotations?|quotation marks?|citations?|emphasis|footnotes?|alterations?|punctuation|modifications?)'
    __MODIFABLE_TYPE = r'(?:internal)'
    __QUOTE_MODIFICATION = r'(?:added|removed|in original|omitted)'
    __OPINION_TYPES = r'(?:dissenting|concurring|plurality|unpublished|per curiam)'
    __SPECIAL_DOCUMENT_TYPES = r'(?:continuance|order)'
    __OPINION_TYPE_MODIFICATION = r'(?:in(?: the)? judgment|in part)'
    __REFERENTIAL = r'(?:quoting|citing|cited in)'

    PARENTHETICAL_REGEX_BLACKLIST_RULES = [
        r'(?:e|i)n banc',  # en banc or in banc
        f'.*J.',  # Scalia, J.
        f'.*J., {__OPINION_TYPES}',  # Scalia, J., dissenting
        f'{__OPINION_TYPES}(?: opinion)?',  # plurality opinion
        f'{__SPECIAL_DOCUMENT_TYPES}',
        r'dictum|dicta',
        r'simplified',
        r'same|similar|contra',
        f'(?:{__MODIFABLE_TYPE} )?{__MODIFIABLE} {__QUOTE_MODIFICATION}',  # internal citations omitted
        f'(?:{__MODIFABLE_TYPE} )?{__MODIFIABLE} and {__MODIFIABLE} {__QUOTE_MODIFICATION}',
        f'(?:{__MODIFABLE_TYPE} )?{__MODIFIABLE}, {__MODIFIABLE}, and {__MODIFIABLE} {__QUOTE_MODIFICATION}',
        f'{__REFERENTIAL} .*',  # citing Gonzales v. Raich, 123 U.S. 456 (2019). A tad over-inclusive but very helpful
        r'.{1,10}\d{4}',  # 2nd Cir. 2019
        r'.{1,15} I+',  # Gonzales II
    ]

    PARENTHETICAL_BLACKLIST_REGEX = re.compile(r'^\s*"?(?:' + r"|".join(
        map(lambda reg: f'(?:{reg})', PARENTHETICAL_REGEX_BLACKLIST_RULES)) + r')"?\s*$', re.IGNORECASE)

    @classmethod
    def is_descriptive(cls, text: str) -> bool:
        text = cls.prepare_text(text)
        return not re.match(cls.PARENTHETICAL_BLACKLIST_REGEX, text)

    @classmethod
    def prepare_text(cls, text: str) -> str:
        text = re.sub(r'\* \d+', ' ', text)  # Remove star page numbers (e.g. *389)
        text = re.sub(r'\s+', ' ', text)  # Remove excess whitespace
        return text


if __name__ == '__main__':
    print(ParentheticalProcessor.PARENTHETICAL_BLACKLIST_REGEX.pattern)
