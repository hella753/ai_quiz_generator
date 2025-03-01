from PyPDF2 import PdfReader
from docx2txt import docx2txt  # type: ignore


class FileProcessor:
    """
    Class to process files and extract text from them
    """
    def __init__(self, file):
        self.file = file

    def process_file(self):
        text = ""
        if self.file.name.endswith(".docx") or self.file.name.endswith(".doc"):
            text = self._process_docx()
        if self.file.name.endswith(".pdf"):
            text = self._process_pdfs()
        return text

    def _process_docx(self):
        """
        Process docx files
        :return: text extracted from docx files
        """
        text = docx2txt.process(self.file)
        return text

    def _process_pdfs(self):
        """
        Process PDF files
        :return: text extracted from PDF files
        """
        text = ""
        reader = PdfReader(self.file)
        for page in reader.pages:
            text += page.extract_text()
        return text
