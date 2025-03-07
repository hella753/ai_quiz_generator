from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path


app_name="user"
router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'taken-quiz', TakenQuizViewSet, basename='taken-quiz')
router.register(r'created-quiz', CreatedQuizViewSet, basename='created-quiz')

urlpatterns = router.urls

urlpatterns += [

    path('verify-account/<uuid:token>/', verify_account_view, name='verify-account'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/request/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('forgot-password/reset/<uuid:token>/', ResetPasswordView.as_view(), name='reset-password'),
]