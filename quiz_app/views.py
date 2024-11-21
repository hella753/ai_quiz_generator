from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from quiz_app.permissions import IsCreater
from quiz_app.utils.FileProcessor import FileProcessor
from quiz_app.models import Quiz
from quiz_app.utils.serializer_utils import SerializerFactory
from quiz_app.serializers import QuizSerializer, InputSerializer
from quiz_app.utils import generate_quiz


class QuizViewSet(ModelViewSet):
    serializer_class = SerializerFactory(
        retrieve=QuizSerializer,
        list=QuizSerializer,
        create=InputSerializer,
        default=QuizSerializer,
        update=QuizSerializer
    )

    queryset = Quiz.objects.prefetch_related(
                "questions",
                "questions__answers"
    )

    def get_permissions(self):
        if self.action == "create" or self.action == "list":
            return [IsAuthenticated()]
        if self.action == "update" or self.action == "destroy" or self.action == "partial_update":
            return [IsCreater()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if file:
            text = FileProcessor(file).process_file()
            data = generate_quiz(request.data.get("_input"), text)
        else:
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

