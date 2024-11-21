from PyPDF2 import PdfReader
from docx2txt import docx2txt


class FileProcessor:
    def __init__(self, file):
        self.file = file

    def process_file(self):
        if self.file.name.endswith(".docx") or self.file.name.endswith(".doc"):
            text = self.process_docx()
        if self.file.name.endswith(".pdf"):
            text = self.process_pdfs()
        return text

    def process_docx(self):
        text = docx2txt.process(self.file)
        return text

    def process_pdfs(self):
        text = ""
        reader = PdfReader(self.file)
        for page in reader.pages:
            text += page.extract_text()
        return text