from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, UserQuizViewSet

app_name="user"
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-quiz', UserQuizViewSet, basename='user-quiz')

urlpatterns = router.urls