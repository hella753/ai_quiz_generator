from django.db import models
from django.db.models import Count, F
from django.db.models import Case, When, Value, BooleanField

class UserAnswerManager(models.Manager):
    
    def get_count_of_users_who_took_quize(self, quiz_id):
        return self.filter(question__quiz__id=quiz_id).values('user').distinct().count()

    def get_correct_percentage(self, quiz_id):
        total_users = self.get_count_of_users_who_took_quize(quiz_id)
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
                            incorrect_count=Count(Case(When(correct=False, then=1))),
                            total_answers=Count('id'),
                            incorrect_percentage=F('incorrect_count') * 100.0 / F('total_answers')
                        ) \
                        .order_by('-incorrect_percentage')

        hardest_questions = []
        for question in questions:
            hardest_questions.append({
                'question': question['question__question'],
                'percentage_incorrect': question['incorrect_percentage']
            })
        return hardest_questions