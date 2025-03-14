from typing import Optional, List
from pydantic import BaseModel, field_validator


class Answer(BaseModel):
    """
    This class is used to validate the answers.
    """
    answer: str
    correct: bool


class Question(BaseModel):
    """
    This class is used to validate the questions.
    """
    question: str
    score: float
    answers: list[Answer]


class Quiz(BaseModel):
    """
    This class is used to validate the quiz.
    """
    name: str
    questions: list[Question]

    @field_validator("questions")
    def check_max_questions(cls, v):
        if len(v) > 10:
            raise ValueError("Quiz cannot have more than 10 questions.")
        return v


class AnswerCheck(BaseModel):
    """
    This class is used to validate the answer results.
    """
    question: int
    answer: str
    explanation: Optional[str]  # Explanation can be empty
    correct: bool


class QuizAnswers(BaseModel):
    """
    This class is used to validate the quiz answer check results
    """
    answers: List[AnswerCheck]
    user_total_score: float
