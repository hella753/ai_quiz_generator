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
                 request: Request,
                 view_instance: ModelViewSet) -> None:
        """
        Initialize the service.

        :param request: Request an object.
        :param view_instance: QuizViewSet instance.
        """
        self.request = request
        self.view_instance = view_instance
        self.quiz_data = self._get_quiz_data()

    def _get_quiz_data(self) -> dict:
        """
        Get quiz data from the request.

        :return: Quiz data.
        """
        # If the request contains a file, it will be processed
        # and quiz data will be generated based on the file.
        file = self.request.FILES.get("file")

        topic = self.request.data.get("topic")
        number_of_questions = self.request.data.get("number_of_questions")
        type_of_questions = self.request.data.get("type_of_questions")

        creator_input = (f"Generate a quiz with {number_of_questions} "
                         f"{type_of_questions} questions about {topic}")

        quiz_service = QuizGenerationService()
        try:
            if file:
                return quiz_service.generate_quiz_from_file(
                    file,
                    creator_input
                )
            return quiz_service.generate_quiz_data(creator_input)
        except QuizGenerationError as e:
            return {'error': str(e), 'status': status.HTTP_400_BAD_REQUEST}

    def process_quiz_data(self) -> tuple:
        """
        Process quiz data and create a quiz instance.

        :return: Tuple containing response data, status code and headers.

        :raises QuizGenerationError: If the quiz generation fails.
        """
        try:
            if 'error' in self.quiz_data:
                return self.quiz_data, self.quiz_data['status'], None
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
