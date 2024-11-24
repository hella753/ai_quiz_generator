from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

app_name = "quiz"

router = DefaultRouter()

router.register(r"quiz", QuizViewSet, basename="quiz")
router.register("check-answers", CheckAnswersViewSet, basename="check-answers")


urlpatterns = [
    path("", include(router.urls)),
]
