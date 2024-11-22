from django.contrib import admin
from quiz_app.models import Question, Quiz, Answer, UserAnswer


class QuizAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Quiz, QuizAdmin)


class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Question, QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Answer, AnswerAdmin)


class UserAnswerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(UserAnswer, UserAnswerAdmin)

