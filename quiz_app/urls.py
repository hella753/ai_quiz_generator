from rest_framework.routers import DefaultRouter
from quiz_app.views import QuizViewSet
from django.urls import path, include

app_name="quiz"
router = DefaultRouter()
router.register(r'quizes', QuizViewSet, basename='QuizViewSet')
urlpatterns = [
    path('', include(router.urls)),
]