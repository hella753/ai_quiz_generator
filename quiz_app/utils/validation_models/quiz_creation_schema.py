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
    score: float = 1.0
    answers: list[Answer]


class Quiz(BaseModel):
    """
    This class is used to validate the quiz.
    """
    name: str
    questions: list[Question]

    @field_validator("questions")
    @classmethod
    def check_max_questions(cls, v):
        if len(v) > 10:
            raise ValueError("Quiz cannot have more than 10 questions.")
        return v


creation_schema_str = """
{
    "name": "<string>",
    "questions": [
        {
            "question": "<string>",
            "score": 1.0,
            "answers": [
                {
                    "answer": "<string>",
                    "correct": <bool>
                }
            ]
        }
    ]
}
"""