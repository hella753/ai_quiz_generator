from django.contrib.auth import login
from django.db.models import OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import UpdateAPIView
from rest_framework.mixins import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from quiz_app.permissions import IsThisUser, IsCreater, CanSeeAnalysis
from quiz_app.utils.paginators import CustomPaginator
from quiz_app.utils import SerializerFactory
from quiz_app.utils.helpers.email_sender import EmailSender
from .serializers import *


class CreateUserViewSet(CreateModelMixin, GenericViewSet, ListModelMixin):
    """
    This ViewSet is responsible for creating a new user.
    """
    serializer_class = RegistrationSerializer
    pagination_class = CustomPaginator
    queryset = User.objects.all()

    # def get_permissions(self):
    #     if self.action != "create":
    #         return [IsAuthenticated()]
    #     else:
    #         return []

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False
        user.save()
        token = VerificationToken.objects.create(user=user)
        self.send_verification_mail(user, token)

    def send_verification_mail(self, user, token):
        verification_url = f"{self.request.build_absolute_uri('/')[:-1]}/accounts/verify-account/{token.token}/"
        subject = "Account Verification"
        message = f"""
        Hi, {user.username},

        Please verify your account by clicking on the link below:
        {verification_url}

        This link will expire in 48 hours.

        Regards,
        Team Interpredators
        """

        EmailSender(
            subject=subject,
            message=message,
            to=[user.email]
        ).send_email()


class TakenQuizViewSet(ReadOnlyModelViewSet):
    """
    This ViewSet is responsible for getting the quizzes taken by the user.
    """
    serializer_class = UserQuizSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method is responsible for getting the quizzes
        with scores taken by the user.
        """
        queryset = Quiz.objects.filter(
            questions__your_answers__user=self.request.user
        ).distinct().annotate(
            your_score=QuizScore.objects.filter(
                quiz=OuterRef("pk"), user=self.request.user
            ).values("score")
        )
        return queryset


class CreatedQuizViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
):
    """
    This ViewSet is responsible for getting quizzes created by the user.
    """
    serializer_class = SerializerFactory(
        default=QuizForCreatorSerializer,
        retrieve=CreatedQuizeDeatilSerializer,
        list=QuizForCreatorSerializer,
    )
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, IsCreater]

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            return Quiz.objects.filter(creator=self.request.user)
        return Quiz.objects.none()

    def get_permissions(self):
        if self.action == "retrieve":
            return [CanSeeAnalysis()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions"),
            pk=pk
        )
        self.check_object_permissions(self.request, quiz)
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

    @action(detail=True, methods=["get"], url_path="analytics", permission_classes=[IsCreater], )
    def analytics(self, request, pk=None):
        """
        This action is responsible for getting the analytics of the quiz.
        """
        quiz = get_object_or_404(Quiz, pk=pk, creator=request.user)

        total_users = (UserAnswer.objects.get_count_of_users_who_took_quiz(quiz.id))
        correct_percentage = (UserAnswer.objects.get_correct_percentage(quiz.id))
        hardest_questions = (UserAnswer.objects.get_hardest_questions(quiz.id))

        analytics_data = {
            "total_users": total_users,
            "correct_percentage": correct_percentage,
            "hardest_questions": hardest_questions,
        }

        return Response(analytics_data, status=status.HTTP_200_OK)


def verify_account_view(request, token):
    try:
        verification_token = VerificationToken.objects.get(token=token)

        if not verification_token.is_valid():
            return HttpResponse("<h1>Verification Failed</h1><p>Verification link has expired.</p>")

        user = verification_token.user
        user.is_active = True
        user.save()

        verification_token.delete()

        return HttpResponse(
            "<h1>Account Verified</h1><p>Your account has been successfully verified. You can now log in to the application.</p>")

    except VerificationToken.DoesNotExist:
        return HttpResponse("<h1>Verification Failed</h1><p>Invalid verification token.</p>")


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)