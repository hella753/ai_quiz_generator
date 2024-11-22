from quiz_app.models import Question, Answer


class QuizUpdater:
    def __init__(self, instance, validated_data):
        self.instance = instance
        self.validated_data = validated_data
        self.questions = self.validated_data.pop("questions")

    def update_first_level_fields(self):
        self.instance.name = self.validated_data.get("name")
        self.instance.save()

    def handle_questions(self):
        existing_questions = [question.id for question in self.instance.questions.all()]
        new_questions = [question.get('id') for question in self.questions]
        for question_id in existing_questions:
            if question_id not in new_questions:
                self.instance.questions.filter(id=question_id).delete()

        for question in self.questions:
            question_id = question.get("id")
            if question_id in existing_questions:
                quest = self.instance.questions.get(id=question_id)
                quest.question = question["question"]
                quest.score = question["score"]
                quest.save()
            else:
                quest = Question.objects.create(quiz=self.instance, **question)

            self.handle_answers(quest, question)
        return self.instance

    def handle_answers(self, quest, question):
        answers = question.pop("answers")
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
