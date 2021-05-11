from typing import BinaryIO
import pdftotext


class PdfEngine:
    file: BinaryIO

    def __init__(self, file: BinaryIO):
        self.file = file

    def get_text(self) -> str:
        return "\n\n".join(pdftotext.PDF(self.file))
