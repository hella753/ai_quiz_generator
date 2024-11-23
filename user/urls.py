from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, CreatedQuizViewSet

app_name="user"
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-quiz', CreatedQuizViewSet, basename='user-quiz')

urlpatterns = router.urls