from rest_framework.routers import DefaultRouter
from quiz_app.views import QuizViewSet, CheckAnswersView,QuizAnalysisViewSet
from django.urls import path, include

app_name = "quiz"

router = DefaultRouter()

router.register(r"quizes", QuizViewSet, basename="QuizViewSet")
router.register("check-answers", CheckAnswersView, basename="check-answers")
router.register(r'Quiz-Analysis', QuizAnalysisViewSet,basename="QuizAnalysisViewSet")


urlpatterns = [
    path("", include(router.urls)),
]
