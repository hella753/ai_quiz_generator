from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from quiz_app.permissions import IsCreater
from quiz_app.utils.file_processor import FileProcessor
from quiz_app.models import Quiz
from quiz_app.utils.ai_generator import QuizGenerator
from quiz_app.utils.serializer_utils import SerializerFactory
from quiz_app.serializers import QuizSerializer, InputSerializer


class QuizViewSet(ModelViewSet):
    serializer_class = SerializerFactory(
        retrieve=QuizSerializer,
        list=QuizSerializer,
        create=InputSerializer,
        default=QuizSerializer,
        update=QuizSerializer
    )

    def get_queryset(self):
        if self.action != "list":
            return Quiz.objects.prefetch_related(
                "questions",
                "questions__answers"
            )

    def get_permissions(self):
        for_users = ["create", "list"]
        for_creators = ["update", "destroy", "partial_update"]
        if self.action in for_users:
            return [IsAuthenticated()]
        if self.action in for_creators:
            return [IsCreater()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        creator_input = request.data.get("_input")
        quiz_generator = QuizGenerator(creator_input)

        if file:
            text = FileProcessor(file).process_file()
            data = quiz_generator.generate_quiz(text)
        else:
            data = quiz_generator.generate_quiz()

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
