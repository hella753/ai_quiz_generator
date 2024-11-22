from rest_framework.routers import DefaultRouter
from quiz_app.views import QuizViewSet, CheckAnswersView
from django.urls import path, include

app_name="quiz"
router = DefaultRouter()
router.register(r'quizes', QuizViewSet, basename='QuizViewSet')
router.register('check-answers', CheckAnswersView, basename='check-answers')
urlpatterns = [
    path('', include(router.urls)),
]