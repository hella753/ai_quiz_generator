from django.conf import settings
from django.contrib.auth import login
from django.core.mail import EmailMessage
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
        message = (f"Greetings and welcome to AI quiz maker! "
                   f"We are delighted to see you as a part "
                   f"of our community. Feel free to discover, "
                   f"interact, and collaborate with us to create "
                   f"something wonderful.")
        mail = EmailMessage(
            f"Welcome To AI Quiz Generator {user.username}",
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        mail.send(fail_silently=False)
        if user:
            login(self.request, user)
        else:
            return super().perform_create(serializer)
