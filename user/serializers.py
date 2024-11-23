import re
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer
from quiz_app.models import Answer, Question, Quiz, UserAnswer
from quiz_app.serializers import AnswerSerializer
from user.models import User
from exceptions import DanyTornikeException


class RegistrationSerializer(ModelSerializer):
    """
    Serializer for registration
    """
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate(self, data):
        """
        Raise Custom Exception if username is tornike
        """
        username = data.get("username")
        normalized_username = re.sub(r"[^a-zA-Z]", "", username).lower()
        if normalized_username == "tornike":
            raise DanyTornikeException()
        return super().validate(data)


class UserAnswerSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        exclude = ["question", "created_at", "updated_at", "user", "guest"]

    def get_score(self, obj):
        return obj.get_score()


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
        exclude = ["created_at", "updated_at"]


class QuizForCreatorSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz for creator personal account
    """
    class Meta:
        model = Quiz
        exclude = ["created_at", "updated_at"]


class CreatedQuizeDeatilSerializer(serializers.Serializer):
    """
    Serializer for quiz detail for creator personal account
    """
    id = serializers.CharField()
    name = serializers.CharField()
    creator = serializers.CharField()
    total_score = serializers.IntegerField()
    users_count = serializers.IntegerField()
    users = serializers.ListField(child=serializers.DictField())


class HardestQuestionSerializer(serializers.Serializer):
    """
    Serializer for hardest questions analysis
    """
    question = serializers.CharField()
    percentage_incorrect = serializers.FloatField()


class QuizAnalysisSerializer(serializers.Serializer):
    """
    Serializer for quiz analysis
    """
    count_of_users_who_took_quiz = serializers.IntegerField()
    correct_percentage = serializers.FloatField()
    hardest_questions = HardestQuestionSerializer(many=True)
