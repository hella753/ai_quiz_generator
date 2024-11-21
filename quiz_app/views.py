from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from quiz_app.models import Quiz
from quiz_app.serializer_utils import SerializerFactory
from quiz_app.serializers import QuizSerializer, InputSerializer
from quiz_app.utils import generate_quiz


class QuizViewSet(ModelViewSet):
    serializer_class = SerializerFactory(
        retrieve=QuizSerializer,
        list=QuizSerializer,
        create=InputSerializer,
        default=QuizSerializer
    )

    def get_queryset(self):
        if self.action == "list" or self.action == "retrieve":
            return Quiz.objects.prefetch_related(
                "questions",
                "questions__answers"
            )

    def get_permissions(self):
        if self.action == "create" or self.action == "list":
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        data = generate_quiz(request.data.get("_input"))
        if data != {}:
            serializer = QuizSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(
            {},
            status=status.HTTP_400_BAD_REQUEST
        )

