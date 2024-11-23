from rest_framework.routers import DefaultRouter
from quiz_app.views import QuizViewSet, CheckAnswersViewSet, QuizAnalysisViewSet
from django.urls import path, include

app_name = "quiz"

router = DefaultRouter()

router.register(r"quiz", QuizViewSet, basename="quiz")
router.register("check-answers", CheckAnswersViewSet, basename="check-answers")
router.register(r'quiz-analysis', QuizAnalysisViewSet,basename="quiz-analysis")


urlpatterns = [
    path("", include(router.urls)),
]
