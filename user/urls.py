from rest_framework.routers import DefaultRouter
from user.views import UserViewSet,UsersQuizzesView

app_name="user"
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'users-quizzse', UsersQuizzesView, basename='UsersQuizzesView')

urlpatterns = router.urls