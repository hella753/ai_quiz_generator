from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from quiz_app.permissions import IsCreater
from quiz_app.utils.file_processor import FileProcessor
from quiz_app.models import Quiz, Question, Answer
from quiz_app.utils.ai_generator import QuizGenerator
from quiz_app.utils.serializer_utils import SerializerFactory
from quiz_app.serializers import QuizSerializer, InputSerializer, UserAnswerSerializer
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
import json


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
        quiz_generator = QuizGenerator()

        if file:
            text = FileProcessor(file).process_file()
            data = quiz_generator.generate_quiz(creator_input, text)
        else:
            data = quiz_generator.generate_quiz(creator_input)

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


class CheckAnswersView(CreateModelMixin, GenericViewSet):
    queryset = Quiz.objects.select_related('creator')
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        front_request = request.data.get('_user_answers', [])
        user = request.data.get("guest")
        front_request = json.loads(front_request)
        quiz_generator = QuizGenerator()
        data = []
        for answer in front_request:
            question = (Question.objects.select_related('quiz')
                        .filter(id=int(answer["question_id"]))
                        .first())
            item = {
                "answer": answer["answer"],
                "question": question.question,
                "question_id": question.id,
            }
            data.append(item)

        results = quiz_generator.check_answers(str(data))

        if request.user.is_authenticated:
            answers = [
                Answer(**item, user=request.user) for item in results
            ]
            Answer.objects.bulk_create(answers)
            return Response(results, status=status.HTTP_201_CREATED)
        else:
            if user:
                request.session["guest_user_name"] = user
            guest_name = request.session.get('guest_user_name')
            answers = [
                Answer(**item, guest=guest_name) for item in results
            ]
            Answer.objects.bulk_create(answers)
            return Response(results, status=status.HTTP_201_CREATED)
