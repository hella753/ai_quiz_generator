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

    def get_hardest_questions(self, quiz_id):
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
        from .models import UserAnswer

        user_answers = (
            UserAnswer.objects.filter(question__quiz=quiz)
            .select_related('user', 'question')
        )

        if not user_answers:
            return []

        users = {}
        for answer in user_answers:
            participant_key = (
                answer.user.id if answer.user
                else f"guest-{answer.guest}"
            )

            if participant_key not in users:
                user_data = (
                    {
                        "id": answer.user.id,
                        "username": answer.user.username,
                        "email": answer.user.email,
                    }
                    if answer.user
                    else {"guest": answer.guest}
                )
                users[participant_key] = {
                    "user": user_data,
                    "answers": [],
                }

            users[participant_key]["answers"].append({
                "question_id": answer.question.id,
                "answer": answer.answer,
                "correct": answer.correct,
                "explanation": answer.explanation,
            })

        return list(users.values())
