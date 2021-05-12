from typing import BinaryIO, Iterable
import pdftotext


class PdfEngine:
    file: BinaryIO

    def __init__(self, file: BinaryIO):
        self.file = file

    def get_text(self) -> str:
        pdf_pages_text: Iterable[str] = pdftotext.PDF(self.file)
        # TODO: Make the newline replacement smarter to handle dashes etc.
        return "\n".join(page_text.replace("\n", " ") for page_text in pdf_pages_text)
