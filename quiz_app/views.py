import json
from typing import Dict
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin
from user.serializers import QuizScoreSerializer
from .exceptions import QuizGenerationError
from .utils.filtersets import QuizFilter
from .utils.serializer_utils import SerializerFactory
from .utils.paginators import CustomPaginator
from .utils.ai_generator import QuizGenerator
from .utils.file_processor import FileProcessor
from .utils.email_sender import EmailSender
from .permissions import IsCreater
from .serializers import *


class QuizViewSet(ModelViewSet):
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
    filterset_class = QuizFilter

    permission_classes_map = {
        "create": [IsAuthenticated()],
        "list": [IsAuthenticated()],
        "update": [IsCreater()],
        "destroy": [IsCreater()],
        "partial_update": [IsCreater()]
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

        :raises QuizGenerationError: If the quiz generation fails.
        """
        # If the request contains a file, it will be processed
        # and quiz data will be generated based on the file.
        file = request.FILES.get("file")

        creator_input = request.data.get("_input")
        try:
            data = self._generate_quiz_data(file, creator_input)
            if not data:
                return Response(
                    {},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return self._process_valid_quiz_data(data, request)
        except QuizGenerationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _generate_quiz_data(file: InMemoryUploadedFile,
                            creator_input: str) -> Dict:
        """
        Generate quiz data based on file and/or creator input.

        :param file: File to use for quiz generation.
        :param creator_input: User input for quiz generation.

        :return: Quiz data.
        """
        quiz_generator = QuizGenerator()
        text = FileProcessor(file).process_file() if file else None
        return quiz_generator.generate_quiz(creator_input, text)

    def _process_valid_quiz_data(self,
                                 data: Dict,
                                 request: Request) -> Response:
        """
        Process valid quiz data and return response.

        :param data: Quiz data.
        :param request: Request object.

        :return: Response object.
        """
        serializer = QuizSerializer(
            data=data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )


class CheckAnswersViewSet(CreateModelMixin, GenericViewSet):
    queryset = Quiz.objects.select_related('creator')
    serializer_class = AnswerCheckerSerializer

    def create(self, request, *args, **kwargs):
        answer_data = request.data.get('_user_answers', [])
        guest = request.data.get("guest")
        answer_data = json.loads(answer_data)
        data = []
        quiz = Question.objects.filter(
            id=int(answer_data[0]["question_id"])
        ).first().quiz
        quiz_creator = quiz.creator
        for answer in answer_data:
            question = (Question.objects.select_related('quiz')
                        .filter(id=int(answer["question_id"]))
                        .first())
            item = {
                "answer": answer["answer"],
                "question": question.question,
                "question_id": question.id,
                "question_score": question.score
            }
            data.append(item)
        results = QuizGenerator().check_answers(str(data))
        answers = results["answers"]
        score = results["user_total_score"]
        serializer = QuizScoreSerializer(
            data={
                "quiz": quiz.id,
                "score": score
            },
            context={"request": request, "guest": guest}
        )
        if serializer.is_valid():
            serializer.save()

        answers = [
            {**item, "question": item.pop("question_id")} for item in answers
        ]

        serializer = UserAnswerCheckerSerializer(
            data=answers,
            many=True,
            context={"request": request, "guest": guest}
        )
        if serializer.is_valid():
            serializer.save()

        if guest:
            user = guest
        else:
            user = request.user.username
        EmailSender(
            "Somebody took the quiz!",
            f"{user} took the quiz. Visit the website for more information",
            [quiz_creator.email]
        ).send_email()
        return Response(results, status=status.HTTP_201_CREATED)
