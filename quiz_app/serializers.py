import re
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
    topic_in_preferred_language = serializers.CharField(max_length=150, required=False)
    file = serializers.FileField(required=False)
    language = serializers.CharField(max_length=50, required=False)

    def validate(self, data):
        """
        Validate the input data
        """
        number_of_questions = int(data.get("number_of_questions"))
        type_of_questions = data.get("type_of_questions")
        language = data.get("language")
        topic = data.get("topic_in_preferred_language")
        file = data.get("file")

        if not file and not topic:
            raise serializers.ValidationError(
                "One of the fields should be provided (file or topic)"
            )
        if file and topic:
            raise serializers.ValidationError(
                "Only one of the fields should be provided (file or topic)"
            )
        if file and language:
            raise serializers.ValidationError(
                "Language should not be provided when file is uploaded"
            )
        if number_of_questions > 10 or number_of_questions < 1:
            raise serializers.ValidationError(
                "Number of questions should be greater than 1 and less than 10"
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
    explanation_language_in_english = serializers.CharField(
        max_length=50,
        required=False
    )
    guest = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True
    )

    def validate(self, data):
        """
        Validate the data.
        """
        guest = self.context.get("guest")
        explanation_language = data.get("explanation_language")

        if explanation_language and explanation_language.lower() not in supported_languages:
            raise serializers.ValidationError(
                "Language not supported"
            )

        if guest:
            normalized_username = re.sub(r"[^a-zA-Z]", "", guest).lower()
            if normalized_username == "tornike":
                raise DenyTornikeException()
        return super().validate(data)
