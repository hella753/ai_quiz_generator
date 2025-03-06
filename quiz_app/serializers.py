import re
from django.db import transaction
from rest_framework import serializers
from exceptions import DenyTornikeException
from .models import *
from .utils.quiz_modifier import QuizCreator, QuizUpdater


class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Answer
        exclude = ["question", "created_at", "updated_at"]


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        exclude = ["quiz", "created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        exclude = ["creator", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a quiz with questions and answers
        """
        user = self.context.get("request").user
        return QuizCreator(validated_data, user).create()

    def update(self, instance, validated_data):
        """
        Update a quiz and its related questions and answers.
        """
        return QuizUpdater(instance, validated_data).update()


class InputSerializer(serializers.Serializer):
    """
    Serializer for quiz generating input data
    """
    type_of_questions = serializers.ChoiceField(
        choices=["multiple choice", "open"],
    )
    number_of_questions = serializers.IntegerField()
    topic = serializers.CharField(max_length=150)
    file = serializers.FileField(required=False)

    def validate(self, data):
        """
        Validate the input data
        """
        number_of_questions = int(data.get("number_of_questions"))
        type_of_questions = data.get("type_of_questions")

        if number_of_questions > 10 or number_of_questions < 1:
            raise serializers.ValidationError(
                "Number of questions should be greater than 0 and less than 10"
            )

        if type_of_questions not in ["multiple choice", "open"]:
            raise serializers.ValidationError(
                "Type of quiz should be either multiple choice or open"
            )
        return data


class AnswerItemSerializer(serializers.Serializer):
    """
    Serializer for individual answer items within the submission.
    """
    question_id = serializers.IntegerField(min_value=1)
    answer = serializers.CharField(allow_blank=True)
    question = serializers.CharField(max_length=250)
    question_score = serializers.DecimalField(max_digits=5, decimal_places=2)


class AnswerCheckerSerializer(serializers.Serializer):
    """
    Serializer for checking user answers input data
    """
    _user_answers = serializers.ListField(
        child=AnswerItemSerializer(),
        min_length=1,
        error_messages={
            'min_length': 'At least one answer must be provided',
            'empty': 'No answers provided'
        }
    )
    guest = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate(self, data):
        """
        Validate answer data with improved checks.
        """
        guest = self.context.get("guest")
        if guest:
            normalized_username = re.sub(r"[^a-zA-Z]", "", guest).lower()
            if normalized_username == "tornike":
                raise DenyTornikeException()
        return super().validate(data)


#
# {
#     "_user_answers": [
# {"question_id": 29, "answer": "70", "question": "What is the sum of 23 and 47?", "question_score": 1.00},
# {"question_id": 30, "answer": "2<x<12", "question": "If a triangle has two sides measuring 5 cm and 7 cm, what could be the length of the third side?", "question_score": 1.00},
# {"question_id": 31, "answer": "8*3", "question": "Explain how you would find the area of a rectangle with a length of 8 cm and a width of 3 cm.", "question_score": 1.00},
# {"question_id": 32, "answer": "7", "question": "If you have 10 apples and you give 3 to a friend, how many apples do you have left?", "question_score": 1.00}
# ],
#     "guest": ""
# }