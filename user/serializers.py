import re

from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import *
from exceptions import DenyTornikeException

from quiz_app.models import Question, Quiz, UserAnswer, QuizScore
from quiz_app.serializers import AnswerSerializer


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
        Validate the password and raise the
        Custom Exception if the username is tornike.
        """
        username = data.get("username")
        password = data.get("password")

        normalized_username = re.sub(r"[^a-zA-Z]", "", username).lower()
        if normalized_username == "tornike":
            raise DenyTornikeException()

        if password:
            validate_password(password)
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
    """
    The Purpose of this serializer is to display taken quizzes.
    """
    questions = UserQuestionSerializer(many=True)
    your_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Quiz
        exclude = ["created_at", "updated_at"]


class QuizScoreSerializer(serializers.ModelSerializer):
    """
    The Purpose of this serializer is to create and validate quiz scores.
    """

    class Meta:
        model = QuizScore
        exclude = ["user", "guest"]

    def create(self, validated_data):
        request = self.context.get("request")
        guest = self.context.get("guest")
        quiz = validated_data.get("quiz")
        score = validated_data.get("score")

        with transaction.atomic():
            if request.user.is_authenticated:
                return QuizScore.objects.create(
                    user=request.user,
                    quiz=quiz,
                    score=score
                )
            else:
                if guest:
                    request.session["guest_user_name"] = guest
                else:
                    unique_id = uuid.uuid4()
                    request.session["guest_user_name"] = f"Guest-{unique_id}"

                request.session.modified = True
                guest_name = request.session["guest_user_name"]

                return QuizScore.objects.create(
                    guest=guest_name,
                    quiz=quiz,
                    score=score
                )
                return quiz_score


    def validate(self, data):
        request = self.context.get("request")
        quiz = data.get("quiz")
        if request.user.is_authenticated:
            if QuizScore.objects.filter(user=request.user, quiz=quiz).exists():
                raise ValidationError("You have already taken this quiz")
        return super().validate(data)


class QuizForCreatorSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz for a creator personal account
    """

    class Meta:
        model = Quiz
        exclude = ["created_at", "updated_at"]


class CreatedQuizDetailSerializer(serializers.Serializer):
    """
    Serializer for quiz detail for a creator personal account
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
    hardest_questions = HardestQuestionSerializer(many=True)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password of the user.
    """
    password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128,
                                         write_only=True,
                                         validators=[validate_password])
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError(
                {"password": "Incorrect Password"}
            )

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match"}
            )
        return attrs
