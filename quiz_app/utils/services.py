import logging
import uuid
from typing import Optional, List, Dict

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from quiz_app.exceptions import QuizGenerationError
from quiz_app.models import Question, Quiz, UserAnswer
from quiz_app.serializers import QuizSerializer
from quiz_app.utils import QuizGenerator, FileProcessor
from quiz_app.utils.helpers.email_sender import EmailSender
from user.serializers import QuizScoreSerializer


logger = logging.getLogger(__name__)


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


class QuizSubmissionCheckerService:
    """
    Service for checking quiz submissions.
    """

    def process_quiz_submission(self, request: Request, data: dict) -> dict:
        """
        Process quiz submissions and return graded results.

        :param request: Request object.
        :param data: Submitted quiz data.

        :return: Graded results.
        """
        answer_data = data.get('_user_answers', [])
        is_guest = data.get('guest', False)
        if not answer_data:
            return {"error": "No answers provided", "user_total_score": 0, "answers": []}

        # Get the Quiz Object
        first_question = answer_data[0].get("question_id")
        quiz = Question.objects.get(id=first_question).quiz

        # Check the answers and save the results
        results = QuizGenerator().check_answers(str(answer_data))
        graded_answers = results.get("answers", [])
        total_score = results.get("user_total_score", 0)

        # Save the Score and User Answers
        self._save_quiz_score(quiz.id, total_score, request, is_guest)
        self._save_user_answers(graded_answers, request, is_guest)
        # Send email notification to the quiz creator
        self._notify_quiz_creator(quiz, is_guest if is_guest else request.user.username)
        return results

    @staticmethod
    def _save_quiz_score(quiz_id: uuid, score: float, request: Request, is_guest: bool) -> None:
        """
        Save the user's quiz score.

        :param quiz_id: Quiz ID.
        :param score: User's score.
        :param request: Request object.
        :param is_guest: Guest user flag.
        """
        serializer = QuizScoreSerializer(
            data={"quiz": quiz_id, "score": score},
            context={"request": request, "guest": is_guest}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

    @staticmethod
    def _save_user_answers(graded_answers: List[Dict], request: Request, is_guest: bool) -> None:
        """
        Save graded answers.

        :param graded_answers: List of graded answers.
        :param request: Request an object.
        :param is_guest: Guest user flag.
        """
        user = request.user
        guest = is_guest
        if not graded_answers:
            return

        answers = []
        if user.is_authenticated:
            answers = [UserAnswer(
                user=user, question=Question(id=item.pop("question")), **item
            ) for item in graded_answers]
        else:
            if guest and not request.session.get("guest_user_name"):
                request.session["guest_user_name"] = guest
            guest_name = request.session.get("guest_user_name", guest)
            answers = [UserAnswer(
                guest=guest_name, question=Question(item.pop("question")), **item
            ) for item in graded_answers]

        with transaction.atomic():
            UserAnswer.objects.bulk_create(answers)

    @staticmethod
    def _notify_quiz_creator(quiz: Quiz, user_identifier: str) -> None:
        """
        Notify quiz creator about the submission.

        :param quiz: Quiz object.
        :param user_identifier: User identifier.
        """
        try:
            EmailSender(
                "New Quiz Submission",
                f"{user_identifier} completed your quiz '{quiz.name}'. "
                f"View the results in your dashboard.",
                [quiz.creator.email]
            ).send_email()
        except Exception as e:
            logger.error(f"Failed to send quiz notification: {str(e)}")