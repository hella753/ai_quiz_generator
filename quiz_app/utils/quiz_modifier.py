from typing import Optional, List, Dict, Set
from django.db import transaction
from quiz_app.models import Question, Answer, Quiz


class QuizCreator:
    """
    This class is responsible for creating a new quiz instance.
    """
    def __init__(self, validated_data: dict, user):
        """
        Initializes the QuizCreator with validated data and the creator user.

        :param validated_data: The validated data for quiz creation.
        :param user: The user creating the quiz.
        """
        self.validated_data: dict = validated_data
        self.questions_data: List[Dict] = (
            self.validated_data.pop("questions", [])
        )
        self.user = user

    @transaction.atomic
    def create(self) -> Quiz:
        """
        Creates a new quiz along with its questions and answers.

        :return: The created Quiz instance.
        """
        quiz = Quiz.objects.create(**self.validated_data, creator=self.user)
        self._create_questions(quiz)
        return quiz

    def _create_questions(self, quiz: Quiz) -> None:
        """
        Creates questions and their corresponding answers for a quiz.

        :param quiz: The created quiz instance.
        """
        for question in self.questions_data:
            answers_data = question.pop("answers", [])
            question_obj = Question.objects.create(**question, quiz=quiz)

            Answer.objects.bulk_create([
                Answer(
                    **answer,
                    question=question_obj
                ) for answer in answers_data
            ])


class QuizUpdater:
    """
    This class is responsible for updating the quiz instance.
    """
    def __init__(self, instance: Quiz, validated_data: dict) -> None:
        """
        Initializes the QuizUpdater with the quiz instance and validated data.

        :param instance: The quiz instance being updated.
        :param validated_data: The validated data containing quiz updates.
        """
        self.instance: Quiz = instance
        self.validated_data: dict = validated_data
        self.questions_data: Optional[List[dict]] = (
            self.validated_data.pop("questions", None)
        )

        # Prepare existing questions for comparison
        self.existing_questions: Dict[int, Question] = {
            q.id: q for q in self.instance.questions.all()
        }
        self.existing_question_ids: Set[int] = set(
            self.existing_questions.keys()
        )

    @transaction.atomic
    def update(self) -> Quiz:
        """
        Update the quiz instance and related questions and answers.

        :return: Updated quiz instance
        """
        self._update_quiz_fields()
        if self.questions_data is not None:
            self._handle_questions()
        return self.instance

    def _update_quiz_fields(self) -> None:
        """
        Update the quiz instance fields.
        """
        for attr, value in self.validated_data.items():
            setattr(self.instance, attr, value)
        self.instance.save()

    def _handle_questions(self) -> None:
        """
        Processes the creation, updating, and deletion of questions.
        """
        incoming_question_ids: Set[int] = set()

        if self.questions_data:
            for q_data in self.questions_data:
                self._handle_question(q_data, incoming_question_ids)

        # Delete questions not in the update data
        questions_to_delete: Set[int] = (
                self.existing_question_ids - incoming_question_ids
        )
        if questions_to_delete:
            Question.objects.filter(id__in=questions_to_delete).delete()

    def _handle_question(self,
                         q_data: dict,
                         incoming_question_ids: Set[int]) -> None:
        """
        Handles updating or creating a single question.

        :param q_data: The question data from the request.
        :param incoming_question_ids: A set to track question IDs.
        """
        q_id: Optional[int] = q_data.get('id')
        answers_data: List[dict] = q_data.pop('answers', [])

        if q_id and q_id in self.existing_question_ids:
            # Update existing question

            incoming_question_ids.add(q_id)
            question = self.existing_questions[q_id]
            # Update fields individually
            for key, value in q_data.items():
                if key != 'id':
                    setattr(question, key, value)
            question.save()
        else:
            # Create new question
            question = Question.objects.create(
                quiz=self.instance,
                **{k: v for k, v in q_data.items() if k != 'id'}
            )
            incoming_question_ids.add(question.id)

        # Handle answers for this question
        if answers_data:
            self._handle_answers(question, answers_data)

    def _handle_answers(self,
                        question: Question,
                        answers_data: List[dict]) -> None:
        """
        Handles the creation, updating, and deletion of answers
        for a given question.

        :param question: The question instance related to these answers.
        :param answers_data: List of answer data dictionaries.
        """
        self.existing_answers: Dict[int, Answer] = {
            a.id: a for a in question.answers.all()
        }
        self.existing_answer_ids: Set[int] = set(self.existing_answers.keys())
        self.incoming_answer_ids: Set[int] = set()

        answers_to_create: List[Answer] = []
        for a_data in answers_data:
            self._handle_answer(a_data, question, answers_to_create)

        # Bulk create new answers
        if answers_to_create:
            Answer.objects.bulk_create(answers_to_create)

        # Delete answers not in the update data
        answers_to_delete: Set[int] = (
                self.existing_answer_ids - self.incoming_answer_ids
        )
        if answers_to_delete:
            Answer.objects.filter(id__in=answers_to_delete).delete()

    def _handle_answer(self,
                       a_data: dict,
                       question: Question,
                       answers_to_create: List[Answer]) -> None:
        """
        Handles updating or creating a single answer.

        :param a_data: The answer data from the request.
        :param question: The question instance related to this answer.
        :param answers_to_create: A list of new answers for bulk creation.
        """
        a_id: Optional[int] = a_data.get('id')

        if a_id and a_id in self.existing_answer_ids:
            # Update existing answer
            self.incoming_answer_ids.add(a_id)
            answer = self.existing_answers[a_id]

            # Update fields individually
            for key, value in a_data.items():
                if key != 'id':
                    setattr(answer, key, value)
            answer.save()
        else:
            # Prepare new answer for bulk creation
            answers_to_create.append(
                Answer(
                    question=question,
                    **{k: v for k, v in a_data.items() if k != 'id'}
                )
            )
