import re

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer
from quiz_app.models import Answer, Question, Quiz
from quiz_app.serializers import AnswerSerializer
from user.models import User


class RegistrationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        username = data.get("username")
        normalized_username = re.sub(r'[^a-zA-Z]', '', username).lower()
        if normalized_username == "tornike":
            raise PermissionDenied


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ["question", "created_at", "updated_at"]


class UserQuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    your_answers = UserAnswerSerializer(many=True)

    class Meta:
        model = Question
        exclude = ["quiz", "created_at", "updated_at"]


class UserQuizSerializer(serializers.ModelSerializer):
    questions = UserQuestionSerializer(many=True)

    class Meta:
        model = Quiz
        exclude = ["creator", "created_at", "updated_at"]
