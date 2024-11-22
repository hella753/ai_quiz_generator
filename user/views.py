from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from quiz_app.models import Quiz
from .serializers import UserQuizSerializer
from quiz_app.utils import SerializerFactory
from quiz_app.utils.email_sender import EmailSender
from user.models import User
from user.serializers import RegistrationSerializer


class UserViewSet(ModelViewSet):
    serializer_class = SerializerFactory(
        create=RegistrationSerializer,
        list=RegistrationSerializer,
        retrieve=UserQuizSerializer,
        default=UserQuizSerializer
    )
    queryset = User.objects.all()
    lookup_field = "questions__your_answers__user__username"

    def get_queryset(self):
        if self.action == "retrieve":
            return Quiz.objects.filter(questions__your_answers__user=self.request.user)

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

        EmailSender(
            f"Welcome To AI Quiz Generator {user.username}",
            message,
            [user.email]
        ).send_email()

        if user:
            login(self.request, user)
        else:
            return super().perform_create(serializer)