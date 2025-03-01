from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from quiz_app.exceptions import QuizGenerationError
from quiz_app.serializers import QuizSerializer
from quiz_app.utils import QuizGenerator, FileProcessor


class QuizGenerationService:
    """
    Service for generating quizzes.
    """
    def generate_quiz_from_file(self,
                                file: InMemoryUploadedFile,
                                creator_input: str) -> dict:
        """
        Generate a quiz using file content and creator input
        """
        text = FileProcessor(file).process_file()
        return self.generate_quiz_data(creator_input, text)

    @staticmethod
    def generate_quiz_data(creator_input: str,
                           text: Optional[str] = None) -> dict:
        """
        Generate quiz data based on file and/or creator input.

        :param creator_input: User input for quiz generation.
        :param text: Text content for quiz generation.

        :return: Quiz data.
        """
        quiz_generator = QuizGenerator()
        if text:
            return quiz_generator.generate_quiz(creator_input, text)
        return quiz_generator.generate_quiz(creator_input)


class QuizDataProcessor:
    """
    Service for processing quiz data.
    """
    def __init__(self,
                 quiz_data: dict,
                 request: Request,
                 view_instance: ModelViewSet) -> None:
        """
        Initialize the service.

        :param quiz_data: Quiz data.
        :param request: Request an object.
        :param view_instance: QuizViewSet instance.
        """
        self.quiz_data = quiz_data
        self.request = request
        self.view_instance = view_instance

    def process_quiz_data(self) -> tuple:
        """
        Process quiz data and create a quiz instance.

        :return: Tuple containing response data, status code and headers.
        """
        try:
            if not self.quiz_data:
                return {}, status.HTTP_400_BAD_REQUEST, None
            return self._create_quiz()

        except QuizGenerationError as e:
            return {'error': str(e)}, status.HTTP_400_BAD_REQUEST, None

    def _create_quiz(self) -> tuple:
        """
        Create a quiz instance.

        :return: Tuple containing response data, status code and headers.
        """
        serializer = QuizSerializer(
            data=self.quiz_data,
            context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        self.view_instance.perform_create(serializer)

        return (serializer.data,
                status.HTTP_201_CREATED,
                self.view_instance.get_success_headers(serializer.data))
