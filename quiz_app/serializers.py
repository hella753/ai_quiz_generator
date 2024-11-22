from rest_framework import serializers
from quiz_app.models import Quiz, Question, Answer
from quiz_app.utils.update_quiz import QuizUpdater


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
        questions = validated_data.pop("questions")
        creator = self.context.get("request").user
        quiz = Quiz.objects.create(**validated_data, creator=creator)
        for question in questions:
            answers = question.pop("answers")
            question_obj = Question.objects.create(**question, quiz=quiz)
            answer_list = [
                Answer(**answer, question=question_obj) for answer in answers
            ]
            Answer.objects.bulk_create(answer_list)
            question_obj.answers.set(answer_list)
            quiz.questions.add(question_obj)
        return quiz

    def update(self, instance, validated_data):
        quiz_updater = QuizUpdater(instance, validated_data)
        updated_instance = quiz_updater.handle_questions()
        return updated_instance


class InputSerializer(serializers.Serializer):
    _input = serializers.CharField(max_length=150)
    file = serializers.FileField(required=False)


class UserAnswerSerializer(serializers.Serializer):
    _user_answers = serializers.CharField(max_length=10000)
    guest = serializers.CharField(max_length=30, required=False)

