from rest_framework.routers import DefaultRouter
from quiz_app.views import QuizViewSet, CheckAnswersViewSet
from django.urls import path, include

app_name = "quiz"

router = DefaultRouter()

router.register(r"quiz", QuizViewSet, basename="quiz")
router.register("check-answers", CheckAnswersViewSet, basename="check-answers")


urlpatterns = [
    path("", include(router.urls)),
]
