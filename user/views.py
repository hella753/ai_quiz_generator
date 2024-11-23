from django.contrib.auth import login
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from quiz_app.models import Quiz
from quiz_app.permissions import IsThisUser, IsCreater
from .serializers import UserQuizSerializer
from quiz_app.utils import SerializerFactory
from quiz_app.utils.email_sender import EmailSender
from user.models import User
from user.serializers import (
    RegistrationSerializer,
    CreatedQuizeDeatilSerializer,
    QuizForCreatorSerializer,
)
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from quiz_app.models import UserAnswer


class CreateUserViewSet(CreateModelMixin, GenericViewSet, ListModelMixin):
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action != "create":
            return [IsAuthenticated()]
        else:
            return []

    def perform_create(self, serializer):
        user = serializer.save()
        message = (
            f"Greetings and welcome to AI quiz maker! "
            f"We are delighted to see you as a part "
            f"of our community. Feel free to discover, "
            f"interact, and collaborate with us to create "
            f"something wonderful."
        )

        EmailSender(
            f"Welcome To AI Quiz Generator {user.username}", message, [user.email]
        ).send_email()

        if user:
            login(self.request, user)
        else:
            return super().perform_create(serializer)


class TakenQuizViewSet(GenericViewSet, RetrieveModelMixin):
    serializer_class = UserQuizSerializer
    permission_classes = [IsThisUser]
    queryset = User.objects.all()
    # works on accounts/taken-quiz/username
    lookup_field = "questions__your_answers__user__username"

    def retrieve(self, request, *args, **kwargs):
        user_object = User.objects.filter(username=kwargs[self.lookup_field]).first()

        self.check_object_permissions(self.request, user_object)

        qs = (
            Quiz.objects.select_related("creator")
            .prefetch_related("questions__your_answers", "questions__answers")
            .filter(questions__your_answers__user=request.user)
            .distinct()
        )
        serializer = UserQuizSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class CreatedQuizViewSet(
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):

    serializer_class = SerializerFactory(
        default=QuizForCreatorSerializer,
        retrieve=CreatedQuizeDeatilSerializer,
        list=QuizForCreatorSerializer,
    )
    permission_classes = [IsCreater]

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            return Quiz.objects.filter(creator=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        quiz = get_object_or_404(Quiz.objects.prefetch_related("questions"), pk=pk)
        total_score = quiz.get_total_score()
        users_count = Quiz.objects.get_count_of_who_took_this_quiz(quiz)
        users = Quiz.objects.get_users_who_took_this_quiz(quiz)

        data = {
            "id": str(quiz.id),
            "name": quiz.name,
            "creator": quiz.creator.username,
            "total_score": total_score,
            "users_count": users_count,
            "users": users,
        }

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        url_path="analytics",
        permission_classes=[IsCreater],
    )
    def analytics(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk, creator=request.user)

        total_users = UserAnswer.objects.get_count_of_users_who_took_quiz(quiz.id)
        correct_percentage = UserAnswer.objects.get_correct_percentage(quiz.id)
        hardest_questions = UserAnswer.objects.get_hardest_questions(quiz.id)

        analytics_data = {
            "total_users": total_users,
            "correct_percentage": correct_percentage,
            "hardest_questions": hardest_questions,
        }

        return Response(analytics_data, status=status.HTTP_200_OK)
