from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import User


class Quiz(models.Model):
    name = models.CharField(max_length=150)
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="quizes",verbose_name=_("creator"))

    def __str__(self):
        return f"{self.name}"


class Question(models.Model): 
    question = models.TextField()
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name="questions")  

    def __str__(self):
        return f"{self.question}"


class Answer(models.Model):
    answer = models.TextField()
    correct = models.BooleanField(default=False)
    score = models.DecimalField(decimal_places=2, max_digits=5, default=1)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.answer}"