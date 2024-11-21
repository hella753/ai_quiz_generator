from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import User
import uuid


class Quiz(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name=_("creator")
    )

    def __str__(self):
        return f"{self.name}"


class Question(models.Model):
    question = models.TextField(verbose_name=_("Question"))
    score = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=1,
        verbose_name=_("Score")
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Quiz")
    )

    def __str__(self):
        return f"{self.question}"


class Answer(models.Model):
    answer = models.TextField(verbose_name=_("Answer"))
    correct = models.BooleanField(default=False, verbose_name=_("Correct"))
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Question")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("User")
    )
    guest = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return f"{self.answer}"
