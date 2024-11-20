from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from user.models import User
from user.serializers import RegistrationSerializer


class UserViewSet(ModelViewSet):
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action != "create":
            return [IsAuthenticated()]
        else:
            return []

    def perform_create(self, serializer):
        user = serializer.save()
        if user:
            login(self.request, user)
        else:
            return super().perform_create(serializer)
