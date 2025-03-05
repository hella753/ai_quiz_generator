import logging
from django.db.models import OuterRef
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.generics import UpdateAPIView
from rest_framework.mixins import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.decorators import action

from quiz_app.permissions import IsCreator, CanSeeAnalysis
from quiz_app.utils.paginators import CustomPaginator
from quiz_app.utils import SerializerFactory
from quiz_app.utils.helpers.email_sender import EmailSender

from .utils.helpers import get_verification_email_content
from .utils.services import QuizRetrievalService, QuizAnalyticsService
from .serializers import *


logger = logging.getLogger(__name__)


class UserViewSet(CreateModelMixin, GenericViewSet):
    """
    ViewSet for user registration with email verification.

    Allows anonymous users to create new accounts, which are set to inactive
    until verified through an email link.
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

        EmailSender(
            subject=subject,
            message=message,
            to=[user.email]
        ).send_email()


class TakenQuizViewSet(ReadOnlyModelViewSet):
    """
    This ViewSet is responsible for getting
    the quizzes taken by the user.
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
        ).prefetch_related(
            "questions",
            "questions__answers",
            "questions__your_answers"
        )
        return queryset


class CreatedQuizViewSet(RetrieveModelMixin,
                         ListModelMixin,
                         GenericViewSet):
    """
    This ViewSet is responsible for getting quizzes created by the user.
    """
    serializer_class = SerializerFactory(  # type: ignore
        default=QuizForCreatorSerializer,
        retrieve=CreatedQuizDetailSerializer,
    )
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, IsCreator]

    # Inject services
    quiz_service = QuizRetrievalService()
    analytics_service = QuizAnalyticsService()

    def get_queryset(self):
        """
        This method is responsible for getting the quizzes
        created by the user.
        """
        if self.request.user.is_authenticated:
            return Quiz.objects.filter(creator=self.request.user)
        return Quiz.objects.none()

    def get_permissions(self):
        """
        This method is responsible for getting the permissions
        """
        if self.action == "retrieve":
            return [IsAuthenticated(), CanSeeAnalysis()]
        return super().get_permissions()

    @method_decorator(cache_page(10 * 1))
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
