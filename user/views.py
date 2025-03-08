import logging
from django.db.models import OuterRef
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.generics import UpdateAPIView
from rest_framework.mixins import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.decorators import action

from quiz_app.permissions import IsCreator, CanSeeAnalysis
from quiz_app.tasks import send_email
from quiz_app.utils.paginators import CustomPaginator
from quiz_app.utils import SerializerFactory

from .utils.helpers import (get_verification_email_content,
                            get_reset_email_content)
from .utils.services import QuizRetrievalService, QuizAnalyticsService
from .serializers import *
from rest_framework.views import APIView


logger = logging.getLogger(__name__)


class UserViewSet(CreateModelMixin, GenericViewSet):
    """
    ViewSet for user registration with email verification.

    Allows anonymous users to create new accounts, which are set to inactive
    until verified through an email link.

    create: Register a new user.
    """
    serializer_class = RegistrationSerializer
    pagination_class = CustomPaginator
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Create a new user and send a verification email.

        :param serializer: RegistrationSerializer instance
        """
        user = serializer.save()
        user.is_active = False
        user.save()
        token = VerificationToken.objects.create(user=user)
        self._send_verification_mail(user, token)

    def _send_verification_mail(self,
                                user: User,
                                token: VerificationToken) -> None:
        """
        Email the user with a verification link.

        :param user: User instance
        :param token: VerificationToken instance
        """
        verification_url = (f"{self.request.build_absolute_uri('/')[:-1]}/"
                            f"accounts/verify-account/{token.token}/")
        subject = "Account Verification"
        message = get_verification_email_content(
            user.username,
            verification_url
        )

        send_email.delay(
            subject=subject,
            message=message,
            to=[user.email]
        )


class TakenQuizViewSet(ReadOnlyModelViewSet):
    """
    This ViewSet is responsible for getting
    the quizzes taken by the user.

    list: Get the quizzes taken by the user.
    retrieve: Get detailed information about a specific
    quiz taken by the user.
    """
    serializer_class = UserQuizSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method is responsible for getting the quizzes
        with scores taken by the user.

        :return: Queryset of quizzes taken by the user.
        """
        queryset = Quiz.objects.filter(
            questions__your_answers__user=self.request.user
        ).distinct().annotate(
            your_score=QuizScore.objects.filter(
                quiz=OuterRef("pk"), user=self.request.user
            ).values("score")
        ).prefetch_related(
            "questions",
            "questions__answers",
            "questions__your_answers"
        )
        return queryset


class CreatedQuizViewSet(ReadOnlyModelViewSet):
    """
    This ViewSet is responsible for getting quizzes created by the user.

    list: Get the quizzes created by the user.
    retrieve: Get detailed information about a specific
    quiz created by the user.
    """
    serializer_class = SerializerFactory(  # type: ignore
        default=QuizForCreatorSerializer,
        retrieve=CreatedQuizDetailSerializer,
    )
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, IsCreator]

    quiz_service = QuizRetrievalService()
    analytics_service = QuizAnalyticsService()

    def get_queryset(self):
        """
        This method is responsible for getting the quizzes
        created by the user.

        :return: Queryset of quizzes created by the user.
        """
        if self.request.user.is_authenticated:
            return Quiz.objects.filter(creator=self.request.user)
        return Quiz.objects.none()

    def get_permissions(self):
        """
        This method is responsible for getting the permissions

        :return: List of permissions.
        """
        if self.action == "retrieve":
            return [IsAuthenticated(), CanSeeAnalysis()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve detailed information about a specific quiz.

        :param request: Request object.
        :param args: Arguments.
        :param kwargs: Keyword arguments.
        """
        quiz_id = kwargs.get("pk")
        success, result, status_code = (
            self.quiz_service.get_quiz_detail(quiz_id)
        )
        if not success:
            return Response(result, status=status_code)
        self.check_object_permissions(request, result["quiz"])

        serializer = self.get_serializer(data=result["serializer_data"])
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(10 * 1))
    @action(
        detail=True,
        methods=["GET"],
        url_path="analytics",
        permission_classes=[IsAuthenticated, IsCreator]
    )
    def analytics(self, request, pk=None):
        """
        Get analytics for a specific quiz.

        :param request: Request an object.
        :param pk: Primary key of the quiz.

        :return: Response object.
        """
        success, result, status_code = (
            self.analytics_service.get_quiz_analytics(pk, request.user)
        )
        if not success:
            return Response(result, status=status_code)
        return Response(result, status=status.HTTP_200_OK)


def verify_account_view(request, token):
    """
    This view is responsible for verifying the account of the user.

    :param request: Request object
    :param token: Verification token
    """
    try:
        verification_token = VerificationToken.objects.get(token=token)

        if not verification_token.is_valid():
            return render(
                request,
                "verification_expired.html"
            )

        user = verification_token.user
        user.is_active = True
        user.save()

        verification_token.delete()

        return render(request, "verification_success.html")
    except VerificationToken.DoesNotExist:
        return render(request, "verification_invalid.html")


class ChangePasswordView(UpdateAPIView):
    """
    This view is responsible for changing the password of the user.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        This method is responsible for getting the user object.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        This method is responsible for updating the password of the user.

        :param request: Request an object.
        :param args: Arguments.
        :param kwargs: Keyword arguments.
        """
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    """
    This view is responsible for sending a
    password reset email.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="example@example.com"
                )
            },
            required=['email'],
        ),
        responses={200: openapi.Response("Email has been sent successfully.")}
    )
    def post(self, request):
        """
        This method is responsible for sending a
        password reset email.
        """
        serializer = RequestPasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')

        user = User.objects.filter(email=email).first()
        token = PasswordResetToken.objects.create(user=user)
        self._send_reset_email(user, token)

        return Response(
            {"detail": "Password reset email has been sent."},
            status=status.HTTP_200_OK
        )

    def _send_reset_email(self, user, token):
        """
        Send a password reset email to the user.

        :param user: User instance
        :param token: token instance
        """
        url = (f"{self.request.build_absolute_uri('/')[:-1]}/"
               f"accounts/forgot-password/reset/{token.token}/")
        subject = "Password Reset"
        message = get_reset_email_content(user.username,
                                          url)
        send_email.delay(
            subject=subject,
            message=message,
            to=[user.email]
        )


class ResetPasswordView(APIView):
    """
    This view is responsible for resetting the password.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="NewSecurePassword123"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="NewSecurePassword123"
                )
            },
            required=['new_password', 'confirm_password'],
        ),
        responses={200: openapi.Response(
            "Password has been reset successfully."
        )}
    )
    def post(self, request, token):
        """
        Reset the password of the user.
        """
        serializer = ResetForgottenPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        new_password = serializer.validated_data.get('new_password')

        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token or not reset_token.is_valid():
            return Response({"token": "token has expired"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.delete()
        return Response({"detail": "Password has been reset successfully."},
                        status=status.HTTP_200_OK)
