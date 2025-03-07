import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin

from mixins.error_handling_mixin import ErrorHandlingMixin
from .utils.helpers.serializer_utils import SerializerFactory
from .utils.paginators import CustomPaginator
from .utils.services import QuizDataProcessor, QuizSubmissionCheckerService
from .serializers import *
from .permissions import IsCreator


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
        "partial_update": [IsCreator()]
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

        data_processor = QuizDataProcessor(request, self)
        data, status_code, headers = data_processor.process_quiz_data()
        return Response(data, status=status_code, headers=headers)


class CheckAnswersViewSet(ErrorHandlingMixin,
                          CreateModelMixin,
                          GenericViewSet):
    queryset = Quiz.objects.select_related('creator')
    serializer_class = AnswerCheckerSerializer

    quiz_submission_service = QuizSubmissionCheckerService()

    def create(self, request, *args, **kwargs):
        """
        Process quiz submissions and return graded results.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = (
            self.quiz_submission_service.process_quiz_submission(
                request,
                serializer.validated_data)
        )
        return Response(results, status=status.HTTP_201_CREATED)

