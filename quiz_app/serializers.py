from rest_framework import serializers
from quiz_app.models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Answer
        exclude = ["question"]


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        exclude = ["quiz"]


class UserAnswerSerializer(serializers.Serializer):
    _user_answers = serializers.CharField(max_length=10000)
    guest = serializers.CharField(max_length=30, required=False)


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        exclude = ["creator"]

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
        questions = validated_data.pop("questions")
        instance.name = validated_data.get("name")
        instance.save()

        existing_questions = [question.id for question in instance.questions.all()]
        new_questions = [question.get('id') for question in questions]

        for question_id in existing_questions:
            if question_id not in new_questions:
                instance.questions.filter(id=question_id).delete()

        for question in questions:
            question_id = question.get("id")
            answers = question.pop("answers")

            if question_id in existing_questions:
                quest = instance.questions.get(id=question_id)
                quest.question = question["question"]
                quest.score = question["score"]
                quest.save()
            else:
                quest = Question.objects.create(quiz=instance, **question)

            existing_answers = [answer.id for answer in quest.answers.all()]
            new_answers = [answer.get('id') for answer in answers]

            for answer_id in existing_answers:
                if answer_id not in new_answers:
                    quest.answers.filter(id=answer_id).delete()

            for answer in answers:
                answer_id = answer.get("id")
                if answer_id in existing_answers:
                    ans = quest.answers.get(id=answer_id)
                    ans.answer = answer["answer"]
                    ans.correct = answer["correct"]
                    ans.save()
                else:
                    Answer.objects.create(question=quest, **answer)
        return instance


class InputSerializer(serializers.Serializer):
    _input = serializers.CharField(max_length=150)
    file = serializers.FileField(required=False)
