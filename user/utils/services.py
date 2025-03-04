import logging
from typing import Dict, Any, Tuple
from django.shortcuts import get_object_or_404
from rest_framework import status
from quiz_app.models import Quiz, UserAnswer


logger = logging.getLogger(__name__)


class QuizRetrievalService:
    """
    Service for retrieving quiz data.
    """

    @staticmethod
    def get_quiz_detail(quiz_id) -> Tuple[bool, Dict[str, Any], int]:
        """
        Retrieve detailed quiz information.

        :param quiz_id: ID of the quiz to retrieve.
        :return: Tuple containing (success, data_or_error, status_code)
        """
        try:
            quiz = get_object_or_404(
                Quiz.objects.prefetch_related("questions"),
                pk=quiz_id
            )
            users_count = UserAnswer.objects.get_count_of_users_who_took_quiz(quiz.id)
            users = Quiz.objects.get_users_who_took_this_quiz(quiz)

            quiz_data = {
                "quiz": quiz,
                "serializer_data": {
                    "id": str(quiz.id),
                    "name": quiz.name,
                    "creator": quiz.creator.username,
                    "total_score": quiz.get_total_score(),
                    "users_count": users_count,
                    "users": users,
                }
            }
            return True, quiz_data, status.HTTP_200_OK
        except Quiz.DoesNotExist:
            logger.warning(f"Quiz with ID {quiz_id} not found")
            return (
                False,
                {"error": "Quiz not found"},
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error retrieving quiz {quiz_id}: {str(e)}")
            return (
                False,
                {"error": "An unexpected error occurred"},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizAnalyticsService:
    """
    Service for quiz analytics operations.
    """

    @staticmethod
    def get_quiz_analytics(quiz_id, user) -> Tuple[bool, Dict[str, Any], int]:
        """
        Get analytics data for the specified quiz.

        :param quiz_id: ID of the quiz to retrieve analytics for.
        :param user: User requesting the analytics.

        :return: Tuple containing (success, data_or_error, status_code)
        """
        try:
            quiz = get_object_or_404(Quiz, pk=quiz_id, creator=user)
            total_users = UserAnswer.objects.get_count_of_users_who_took_quiz(
                quiz.id
            )
            hardest_questions = UserAnswer.objects.get_hardest_questions(
                quiz.id
            )
            analytics_data = {
                "total_users": total_users,
                "hardest_questions": hardest_questions
            }
            return True, analytics_data, status.HTTP_200_OK
        except Quiz.DoesNotExist:
            logger.warning(f"Quiz with ID {quiz_id} not found. ")
            return (
                False,
                {"error": "Quiz not found. "},
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error retrieving analytics for quiz "
                             f"{quiz_id}: {str(e)}")
            return (
                False,
                {"error": "An unexpected error occurred"},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )