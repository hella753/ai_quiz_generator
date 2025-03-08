import copy
import logging
from typing import Optional, List, Dict
from uuid import UUID

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from exceptions.custom_exceptions import QuizGenerationError
from quiz_app.models import Question, Quiz, UserAnswer
from quiz_app.serializers import QuizSerializer
from quiz_app.utils import QuizGenerator, FileProcessor

from quiz_app.tasks import send_email
from user.serializers import QuizScoreSerializer


logger = logging.getLogger(__name__)


class QuizGenerationService:
    """
    Service for generating quizzes.
    """
    def generate_quiz_from_file(self,
                                file: InMemoryUploadedFile,
                                language: str,
                                creator_input: str) -> dict:
        """
        Generate a quiz using file content and creator input

        :param file: File object.
        :param language: Language for quiz generation.
        :param creator_input: User input for quiz generation.

        :return: Quiz data.
        """
        text = FileProcessor(file).process_file()
        return self.generate_quiz_data(creator_input, language, text)

    @staticmethod
    def generate_quiz_data(creator_input: str,
                           language: str,
                           text: Optional[str] = None) -> dict:
        """
        Generate quiz data based on file and/or creator input.

        :param creator_input: User input for quiz generation.
        :param language: Language for quiz generation.
        :param text: Text content for quiz generation.

        :return: Quiz data.
        """
        quiz_generator = QuizGenerator()
        if text:
            return quiz_generator.generate_quiz(creator_input, language, text)
        return quiz_generator.generate_quiz(creator_input, language)


class QuizDataProcessor:
    """
    Service for processing quiz data.
    """
    def __init__(self,
                 request: Request,
                 serializer_data: dict,
                 view_instance: ModelViewSet) -> None:
        """
        Initialize the service.

        :param request: Request an object.
        :param view_instance: QuizViewSet instance.
        """
        self.request = request
        self.view_instance = view_instance
        self.serializer_data = serializer_data
        self.quiz_data = self._get_quiz_data()

    def _get_quiz_data(self) -> dict:
        """
        Get quiz data from the request.

        :return: Quiz data.
        """
        # If the request contains a file, it will be processed
        # and quiz data will be generated based on the file.
        file = self.request.FILES.get("file")

        topic = self.serializer_data.get("topic")
        number_of_questions = self.serializer_data.get("number_of_questions")
        type_of_questions = self.serializer_data.get("type_of_questions")
        language = self.serializer_data.get("language")

        creator_input = (f"Generate a quiz in {language} language "
                         f"with {number_of_questions} "
                         f"{type_of_questions} questions about {topic}.")

        quiz_service = QuizGenerationService()
        try:
            if file:
                return quiz_service.generate_quiz_from_file(
                    file,
                    language,
                    creator_input
                )
            return quiz_service.generate_quiz_data(creator_input, language)
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

    def process_quiz_submission(self,
                                request: Request,
                                data: dict) -> dict:
        """
        Process quiz submissions and return graded results.

        :param request: Request object.
        :param data: Submitted quiz data.

        :return: Graded results.
        """
        try:
            answer_data = data.get('_user_answers', [])
            is_guest = data.get('guest', False)
            language = data.get('language', 'English')

            # Get the Quiz Object
            first_question = answer_data[0].get("question_id")

            try:
                quiz = Question.objects.get(id=first_question).quiz
            except Question.DoesNotExist:
                raise ValidationError(
                    f"Question with ID {first_question} does not exist"
                )

            # Check the answers and save the results
            results = QuizGenerator().check_answers(language, str(answer_data))

            ai_results = copy.deepcopy(results)

            graded_answers = results.get("answers", [])
            total_score = results.get("user_total_score", 0)

            # Save the Score and User Answers
            self._save_quiz_score(quiz.id, total_score, request, is_guest)
            self._save_user_answers(graded_answers, request)
            # Send email notification to the quiz creator
            self._notify_quiz_creator(
                quiz, request
            )
            return ai_results
        except ValidationError as e:
            logger.error(
                f"Validation error in quiz submission: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Error processing quiz submission: {str(e)}",
                exc_info=True
            )
            raise ValidationError(
                f"Failed to process quiz submission: {str(e)}"
            )

    @staticmethod
    def _save_quiz_score(quiz_id: UUID,
                         score: float, request: Request,
                         is_guest: bool) -> None:
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
    def _save_user_answers(graded_answers: List[Dict],
                           request: Request) -> None:
        """
        Save graded answers.

        :param graded_answers: List of graded answers.
        :param request: Request an object.
        """
        user = request.user
        if not graded_answers:
            return

        try:
            answers = []
            question_ids = [item.get("question") for item in graded_answers]
            existing_questions = set(Question.objects.filter(
                id__in=question_ids).values_list('id', flat=True))
            if len(existing_questions) != len(question_ids):
                invalid_ids = set(question_ids) - existing_questions
                raise ValidationError(f"Invalid question IDs: {invalid_ids}")

            if user.is_authenticated:
                answers = [UserAnswer(
                    user=user, question=Question(
                        id=item.pop("question")
                    ), **item
                ) for item in graded_answers]
            else:
                guest_name = request.session["guest_user_name"]

                answers = [UserAnswer(
                    guest=guest_name, question=Question(
                        item.pop("question")
                    ), **item
                ) for item in graded_answers]

            with transaction.atomic():
                UserAnswer.objects.bulk_create(answers)

        except IntegrityError as e:
            logger.error(
                f"Integrity error saving answers: {str(e)}",
                exc_info=True
            )
            error_message = str(e)
            if "foreign key constraint" in error_message:
                raise ValidationError(
                    "Question ID or user reference is invalid"
                )
            else:
                raise ValidationError(
                    f"Database integrity error: {error_message}"
                )
        except ValidationError as e:
            logger.error(
                f"Validation error saving answers: {str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error saving answers: {str(e)}",
                exc_info=True
            )
            raise ValidationError(f"Failed to save answers: {str(e)}")

    @staticmethod
    def _notify_quiz_creator(quiz: Quiz,
                             request: Request) -> None:
        """
        Notify quiz creator about the submission.

        :param quiz: Quiz object.
        :param request: Request Object.
        """
        try:
            user = request.user
            if user.is_authenticated:
                user_identifier = user.username
            else:
                user_identifier = request.session["guest_user_name"]

            send_email.delay(
                subject="New Quiz Submission",
                message=f"{user_identifier} completed your quiz '{quiz.name}'. "
                        f"View the results in your dashboard.",
                to=[quiz.creator.email]
            )
        except Exception as e:
            logger.error(f"Failed to send quiz notification: {str(e)}")
