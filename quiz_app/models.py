from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import User
import uuid
from .managers import UserAnswerManager, QuizManager
from django.db.models import Sum


class ModifiedTimeModel(models.Model):
    """
    An abstract base class model that provides
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Quiz(ModifiedTimeModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name=_("creator"),
    )

    def get_total_score(self):
        total_score = self.questions.aggregate(total=Sum("score"))["total"]
        return total_score or 0

    def __str__(self):
        return f"{self.name}"

    objects = QuizManager()


class Question(ModifiedTimeModel):
    question = models.TextField(verbose_name=_("Question"))
    score = models.DecimalField(
        decimal_places=2, max_digits=5, default=1, verbose_name=_("Score")
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Quiz")
    )

    def __str__(self):
        return f"{self.question}"


class Answer(ModifiedTimeModel):
    answer = models.TextField(verbose_name=_("Answer"))
    correct = models.BooleanField(default=False, verbose_name=_("Correct"))
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Question"),
    )

    def __str__(self):
        return f"{self.answer}"


class UserAnswer(ModifiedTimeModel):
    answer = models.TextField(verbose_name=_("Answer"))
    correct = models.BooleanField(default=False, verbose_name=_("Correct"))
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="your_answers",
        verbose_name=_("Question"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_answers",
        verbose_name=_("User"),
    )
    guest = models.CharField(max_length=25, null=True, blank=True)
    explanation = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Explanation")
    )

    objects = UserAnswerManager()

    def __str__(self):
        return f"{self.answer}"

    def get_score(self):
        if self.correct:
            return self.question.score
        return 0.0


class QuizScore(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name=_("Quiz")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_scores",
        verbose_name=_("User")
    )
    score = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=0.0,
        verbose_name=_("Score")
    )

    def __str__(self):
        return f"{self.score}"