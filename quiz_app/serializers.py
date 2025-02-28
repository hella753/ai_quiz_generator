import re
from django.db import transaction
from rest_framework import serializers
from exceptions import DanyTornikeException
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
    _input = serializers.CharField(max_length=150)
    file = serializers.FileField(required=False)


class AnswerCheckerSerializer(serializers.Serializer):
    """
    Serializer for checking user answers input data
    """
    _user_answers = serializers.CharField(max_length=10000)
    guest = serializers.CharField(max_length=30, required=False)


class UserAnswerCheckerSerializer(serializers.ModelSerializer):
    """
    Serializer for creating user answers
    """
    class Meta:
        model = UserAnswer
        fields = "__all__"

    def create(self, validated_data):
        results = validated_data
        if not isinstance(results, list):
            results = [results]
        request = self.context.get("request")
        user = request.user
        guest = self.context.get('guest')
        if user.is_authenticated:
            answers = [
                UserAnswer(**item, user=user) for item in results
            ]
            with transaction.atomic():
                UserAnswer.objects.bulk_create(answers)
        else:
            if guest:
                request.session["guest_user_name"] = guest
            guest_name = request.session.get("guest_user_name")
            answers = [
                UserAnswer(**item, guest=guest_name) for item in results
            ]
            with transaction.atomic():
                UserAnswer.objects.bulk_create(answers)

    def validate(self, data):
        user = self.context.get("request").user
        question = data.get("question")
        guest = self.context.get("guest")
        if user.is_authenticated:
            if UserAnswer.objects.filter(user=user, question=question).exists():
                raise serializers.ValidationError("You have already taken this quiz")
        elif self.context.get("guest"):
            normalized_username = re.sub(r"[^a-zA-Z]", "", guest).lower()
            if normalized_username == "tornike":
                raise DanyTornikeException()
        return super().validate(data)
