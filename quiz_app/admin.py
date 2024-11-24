from django.contrib import admin
from quiz_app.models import Question, Quiz, Answer, UserAnswer, QuizScore


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuizScore)
class QuizScoreAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
