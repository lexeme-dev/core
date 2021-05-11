from typing import BinaryIO
import pdfminer.high_level


class PdfEngine:
    file: BinaryIO

    def __init__(self, file: BinaryIO):
        self.file = file

    def get_text(self) -> str:
        return pdfminer.high_level.extract_text(self.file)
