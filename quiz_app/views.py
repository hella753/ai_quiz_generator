from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from quiz_app.permissions import IsCreater, CanSeeAnalysis
from quiz_app.utils.email_sender import EmailSender
from quiz_app.utils.file_processor import FileProcessor
from quiz_app.models import Quiz, Question, UserAnswer
from quiz_app.utils.ai_generator import QuizGenerator
from quiz_app.utils.serializer_utils import SerializerFactory
from quiz_app.serializers import (
    QuizSerializer,
    InputSerializer, AnswerCheckerSerializer, UserAnswerCheckerSerializer
)
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin,ListModelMixin
import json


class QuizViewSet(ModelViewSet):
    serializer_class = SerializerFactory(
        create=InputSerializer,
        default=QuizSerializer
    )
    queryset = Quiz.objects.prefetch_related(
                "questions",
                "questions__answers"
    ).all()

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
            serializer = QuizSerializer(
                data=data,
                context={"request": request}
            )
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


class CheckAnswersViewSet(CreateModelMixin, GenericViewSet):
    queryset = Quiz.objects.select_related('creator')
    serializer_class = AnswerCheckerSerializer

    def create(self, request, *args, **kwargs):
        answer_data = request.data.get('_user_answers', [])
        guest = request.data.get("guest")
        answer_data = json.loads(answer_data)
        data = []
        quiz_creator = Question.objects.filter(
            id=int(answer_data[0]["question_id"])
        ).first().quiz.creator
        for answer in answer_data:
            question = (Question.objects.select_related('quiz')
                        .filter(id=int(answer["question_id"]))
                        .first())
            item = {
                "answer": answer["answer"],
                "question": question.question,
                "question_id": question.id,
            }
            data.append(item)
        results = QuizGenerator().check_answers(str(data))
        results = [
            {**item, "question": item.pop("question_id")} for item in results
        ]
        serializer = UserAnswerCheckerSerializer(
            data=results,
            many=True,
            context={"request": request, "guest": guest}
        )
        serializer.is_valid(raise_exception=True)
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


# class QuizAnalysisViewSet(ListModelMixin,RetrieveModelMixin, GenericViewSet):
#     queryset = Quiz.objects.all()
#     serializer_class = SerializerFactory(
#         default=QuizSerializer,
#         retrieve=QuizAnalysisSerializer
#     )

#     def get_queryset(self):
#         return Quiz.objects.filter(creator=self.request.user)
    
    
#     def list(self, request, *args, **kwargs):
#         print(self.request.user)
#         return super().list(request, *args, **kwargs)

#     def retrieve(self, request, *args, **kwargs):
#         quiz = self.get_object()
#         print(f"Retrieved quiz: {quiz}")
#         print(self.request.user)

#         count_of_users_who_took_quiz = UserAnswer.objects.get_count_of_users_who_took_quiz(quiz.id)
#         correct_percentage = UserAnswer.objects.get_correct_percentage(quiz.id)
#         hardest_questions = UserAnswer.objects.get_hardest_questions(quiz.id)

#         analysis_data = {
#             "count_of_users_who_took_quiz": count_of_users_who_took_quiz,
#             "correct_percentage": correct_percentage,
#             "hardest_questions": hardest_questions,
#         }

#         serializer = QuizAnalysisSerializer(analysis_data)

#         return Response(serializer.data, status=status.HTTP_200_OK)
