from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from quiz_app.models import Quiz
from quiz_app.serializers import QuizSerializer, InputSerializer
from quiz_app.utils import generate_quiz


class QuizViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuizSerializer
        return InputSerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return Quiz.objects.all()

    def create(self, request, *args, **kwargs):
        data = generate_quiz(request.data.get("_input"))
        serializer = QuizSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
