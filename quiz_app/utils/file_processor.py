from PyPDF2 import PdfReader
from docx2txt import docx2txt


class FileProcessor:
    """
    Class to process files and extract text from them
    """
    def __init__(self, file):
        self.file = file

    def process_file(self):
        text = ""
        if self.file.name.endswith(".docx") or self.file.name.endswith(".doc"):
            text = self.process_docx()
        if self.file.name.endswith(".pdf"):
            text = self.process_pdfs()
        return text

    def process_docx(self):
        """
        Process docx files
        :return: text extracted from docx files
        """
        text = docx2txt.process(self.file)
        return text

    def process_pdfs(self):
        """
        Process pdf files
        :return: text extracted from pdf files
        """
        text = ""
        reader = PdfReader(self.file)
        for page in reader.pages:
            text += page.extract_text()
        return text