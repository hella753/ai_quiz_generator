import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin

from mixins.error_handling_mixin import ErrorHandlingMixin
from .utils.helpers.serializer_utils import SerializerFactory
from .utils.paginators import CustomPaginator
from .utils.services import QuizDataProcessor, QuizSubmissionCheckerService
from .serializers import *
from .permissions import IsCreator, CanSeeAnalysis
from .utils.worksheet import ExportToWorksheet

logger = logging.getLogger(__name__)


class QuizViewSet(ErrorHandlingMixin, ModelViewSet):
    """
    ViewSet for a Quiz model.

    create: Create, save and return a new quiz instance.
    list: Returns a list of all quiz instances.
    retrieve: Returns the specified quiz instance.
    update: Updates and returns the specified quiz instance.
    destroy: Deletes the specified quiz instance.
    partial_update: Partially updates the specified quiz instance.
    """
    serializer_class = SerializerFactory(  # type: ignore
        create=InputSerializer,
        default=QuizSerializer
    )
    pagination_class = CustomPaginator
    queryset = Quiz.objects.prefetch_related(
                "questions",
                "questions__answers"
    ).all()

    permission_classes_map = {
        "create": [IsAuthenticated()],
        "list": [IsAuthenticated()],
        "update": [IsCreator()],
        "destroy": [IsCreator()],
        "partial_update": [IsCreator()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        """
        Get permissions based on action.

        :return: List of permissions.
        """
        return self.permission_classes_map.get(
            self.action,
            super().get_permissions()
        )

    def create(self, request, *args, **kwargs):
        """
        Quiz creation endpoint.

        :param request: Request object.
        :param args: arguments.
        :param kwargs: keyword arguments.

        :return: Response object.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data_processor = QuizDataProcessor(request, serializer.validated_data, self)
        data, status_code, headers = data_processor.process_quiz_data()
        return Response(data, status=status_code, headers=headers)

    @action(detail=True, methods=["get"], permission_classes=[CanSeeAnalysis])
    def export_to_worksheet(self, request, *args, **kwargs):
        """
        Export quiz data to a worksheet.

        :param request: Request object.
        :param args: Arguments.
        :param kwargs: Keyword arguments.

        :return: Response object.
        """
        quiz = self.get_object()
        serializer = self.get_serializer(quiz)
        data = serializer.data
        export_to_worksheet = ExportToWorksheet(request, data)
        response = export_to_worksheet.create_worksheet()
        return Response(response, status=status.HTTP_200_OK)


class CheckAnswersViewSet(ErrorHandlingMixin,
                          CreateModelMixin,
                          GenericViewSet):
    """
    ViewSet for checking quiz answers.

    create: Process quiz submissions and return graded results.
    """
    queryset = Quiz.objects.select_related('creator')
    serializer_class = AnswerCheckerSerializer

    quiz_submission_service = QuizSubmissionCheckerService()

    def create(self, request, *args, **kwargs):
        """
        Process quiz submissions and return graded results.

        :param request: Request object.
        :param args: Arguments.
        :param kwargs: Keyword arguments.

        :return: Response object.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = (
            self.quiz_submission_service.process_quiz_submission(
                request,
                serializer.validated_data)
        )
        return Response(results, status=status.HTTP_201_CREATED)

