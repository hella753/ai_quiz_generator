from django.db import models
from django.db.models import Count, F
from django.db.models import Case, When


class UserAnswerManager(models.Manager):
    """
    Custom manager for UserAnswer model
    """
    def get_count_of_users_who_took_quiz(self, quiz_id):
        return (
            self.filter(question__quiz__id=quiz_id)
            .values('user')
            .distinct()
            .count()
        )

    def get_correct_percentage(self, quiz_id):
        total_users = self.get_count_of_users_who_took_quiz(quiz_id)
        if total_users == 0:
            return 0.0
        all_correct_count = self.filter(
            question__quiz__id=quiz_id,
            correct=True
        ).values('user').distinct().count()
        return (all_correct_count / total_users) * 100

    def get_hardest_questions(self, quiz_id):
        questions = self.filter(question__quiz__id=quiz_id) \
                        .values('question__question') \
                        .annotate(
                            incorrect_count=Count(
                                Case(When(correct=False, then=1))
                            ),
                            total_answers=Count('id'),
                            incorrect_percentage=F(
                                'incorrect_count'
                            ) * 100.0 / F(
                                'total_answers'
                            )
                        ) \
                        .order_by('-incorrect_percentage')

        hardest_questions = []
        for question in questions:
            hardest_questions.append({
                'question': question['question__question'],
                'percentage_incorrect': question['incorrect_percentage']
            })
        return hardest_questions


class QuizManager(models.Manager):
    """
    Custom manager for Quiz model
    """
    def get_count_of_who_took_this_quiz(self, quiz):
        from .models import UserAnswer
        return (
            UserAnswer.objects.filter(question__quiz=quiz)
            .values('user', 'guest')
            .distinct()
            .count()
        )

    def get_users_who_took_this_quiz(self, quiz):
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
