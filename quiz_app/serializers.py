from rest_framework import serializers
from quiz_app.models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ["question"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        exclude = ["quiz"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        exclude = ["creator"]

    def create(self, validated_data):
        questions = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data, creator=self.context.get("request").user)
        for question in questions:
            answers = question.pop("answers")
            question_obj = Question.objects.create(**question, quiz=quiz)
            answer_list = [Answer(**answer, question=question_obj) for answer in answers]
            Answer.objects.bulk_create(answer_list)
            question_obj.answers.set(answer_list)
            quiz.questions.add(question_obj)
        return quiz


class InputSerializer(serializers.Serializer):
    _input = serializers.CharField(max_length=150)
