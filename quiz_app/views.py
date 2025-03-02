import json
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin
from user.serializers import QuizScoreSerializer
from quiz_app.utils.helpers.serializer_utils import SerializerFactory
from .utils.paginators import CustomPaginator
from .utils.ai_generator import QuizGenerator
from quiz_app.utils.helpers.email_sender import EmailSender
from .permissions import IsCreater
from .serializers import *
from .utils.services import QuizDataProcessor


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
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data_processor = QuizDataProcessor(request, self)
        data, status_code, headers = data_processor.process_quiz_data()
        return Response(data, status=status_code, headers=headers)


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
