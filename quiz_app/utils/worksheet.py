import os
from datetime import datetime
import pdfkit
from django.template.loader import get_template
from rest_framework.request import Request


class ExportToWorksheet:
    """
    Export quiz data to a worksheet.
    """
    def __init__(self, request: Request, data: dict):
        """
        Initialize the class.

        :param request: Request an object.
        :param data: Data to be exported.
        """
        self.request = request
        self.data = data
        self.questions = data.get("questions")
        self.quiz_name = data.get("name")

    def _prepare_context(self):
        """
        Prepare context for worksheet.

        :return: Context dictionary.
        """
        context = {
            "quiz_name": self.quiz_name,
            "questions": self.questions,
        }
        return context

    def create_worksheet(self):
        """
        Create a worksheet.

        :return: File url or error message.
        """
        template = get_template("worksheet_template.html")
        context = self._prepare_context()

        output_text = template.render(context)
        config_path = os.getenv("WKHTMLTOPDF_PATH")
        config = pdfkit.configuration(wkhtmltopdf=config_path)

        current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        output_path = f"media/{current_date}-{self.request.user}.pdf"
        pdf_options = {
            'enable-local-file-access': '',
            'user-style-sheet': "static/styles.css",
            'encoding': 'UTF-8',
            'quiet': ''
        }
        try:
            pdfkit.from_string(output_text,
                               output_path,
                               configuration=config,
                               options=pdf_options)
            download_url = (f"{self.request.scheme}://"
                            f"{self.request.get_host()}/"
                            f"{output_path}")
            return {"download_url": download_url}
        except Exception as e:
            return {"error": str(e)}
        return output_path
