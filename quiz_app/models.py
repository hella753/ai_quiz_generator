import uuid
from user.models import User
from .managers import *


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
    name = models.CharField(max_length=150, verbose_name="Name")
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="creator",
    )

    def get_total_score(self):
        total_score = self.questions.aggregate(total=Sum("score"))["total"]
        return total_score or 0

    def __str__(self):
        return f"{self.name}"

    objects = QuizManager()


class Question(ModifiedTimeModel):
    question = models.TextField(verbose_name="Question")
    score = models.DecimalField(
        decimal_places=2, max_digits=5, default=1, verbose_name="Score"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Quiz"
    )

    def __str__(self):
        return f"{self.question}"


class Answer(ModifiedTimeModel):
    answer = models.TextField(verbose_name="Answer")
    correct = models.BooleanField(default=False, verbose_name="Correct")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Question"
    )

    def __str__(self):
        return f"{self.answer}"


class UserAnswer(ModifiedTimeModel):
    answer = models.TextField(verbose_name="Answer")
    correct = models.BooleanField(default=False, verbose_name="Correct")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="your_answers",
        verbose_name="Question",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_answers",
        verbose_name="User",
    )
    guest = models.CharField(max_length=25, null=True, blank=True)
    explanation = models.TextField(
        null=True,
        blank=True,
        verbose_name="Explanation"
    )

    objects = UserAnswerManager()

    def __str__(self):
        return f"{self.answer}"

    def get_score(self):
        if self.correct:
            return self.question.score
        return 0.0


class QuizScore(ModifiedTimeModel):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name="Quiz"
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="quiz_scores",
        verbose_name="User"
    )
    score = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=0.0,
        verbose_name="Score"
    )
    guest = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return f"{self.score}"