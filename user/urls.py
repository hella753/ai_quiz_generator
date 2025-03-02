from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path


app_name="user"
router = DefaultRouter()
router.register(r'create-user', CreateUserViewSet, basename='create-user')
router.register(r'taken-quiz', TakenQuizViewSet, basename='taken-quiz')
router.register(r'created-quiz', CreatedQuizViewSet, basename='created-quiz')

urlpatterns = router.urls

urlpatterns += [path('verify-account/<uuid:token>/', verify_account_view, name='verify-account')]