from django.db import models
from django.db.models import Case, When, Count, F, Sum, IntegerField


class UserAnswerManager(models.Manager):
    """
    Custom manager for UserAnswer model
    """
    def get_count_of_users_who_took_quiz(self, quiz_id):
        """
        Get the count of users who took the quiz

        :param quiz_id: ID of the quiz

        :return: Count of users who took the quiz
        """
        distinct_users = self.filter(
            question__quiz__id=quiz_id
        ).values(
            'user', 'guest'
        ).distinct()
        return distinct_users.count()

    def get_hardest_questions(self, quiz_id) :
        """
        Get the hardest questions in the quiz

        :param quiz_id: ID of the quiz

        :return: List of hardest questions
        """
        quiz_answers = self.filter(question__quiz__id=quiz_id).values(
            "question__question"
        ).annotate(
            total_answers=Count('id'),
            incorrect_count=Sum(Case(
                When(correct=False, then=1),
                default=0,
                output_field=IntegerField()
            )),
            incorrect_percentage=(
                    F('incorrect_count') * 100.0 / F('total_answers')
            )
        ).order_by(
            "-incorrect_percentage"
        ).values(
            'question__question',
            'incorrect_percentage'
        )
        return quiz_answers


class QuizManager(models.Manager):
    """
    Custom manager for a Quiz model
    """

    @staticmethod
    def get_users_who_took_this_quiz(quiz):
        # TODO
        # May be a better way to do this
        from .models import UserAnswer

        user_answers = (
            UserAnswer.objects.filter(question__quiz=quiz)
            .select_related('user', 'question')
        )
        users = {}
        for user_answer in user_answers:
            participant_key = (
                user_answer.user.id if user_answer.user else f"guest-{user_answer.guest}"
            )

            if participant_key not in users:
                users[participant_key] = {
                    "user": {
                        "id": user_answer.user.id if user_answer.user else None,
                        "username": user_answer.user.username if user_answer.user else None,
                        "email": user_answer.user.email if user_answer.user else None,
                    } if user_answer.user else {
                        "guest": user_answer.guest,
                    },
                    "answers": []
            }

            users[participant_key]["answers"].append({
                "question_id": user_answer.question.id,
                "answer": user_answer.answer,
                "correct": user_answer.correct,
                "explanation": user_answer.explanation,
            })

        return list(users.values())
