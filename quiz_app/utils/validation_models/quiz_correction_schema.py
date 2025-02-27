from typing import Optional, List
from pydantic import BaseModel, field_validator


class AnswerCheck(BaseModel):
    """
    This class is used to validate the answer results.
    """
    question_id: int
    answer: str
    explanation: Optional[str] = None  # Explanation can be empty
    correct: bool

    @field_validator('explanation')
    @classmethod
    def validate_explanation(cls, v):
        if v:
            sentences = v.split(".")
            if len(sentences) > 2:
                raise ValueError("Explanation should not exceed two sentences.")
        return v


class QuizAnswers(BaseModel):
    """
    This class is used to validate the quiz answer check results
    """
    answers: List[AnswerCheck]
    user_total_score: float


quiz_correction_schema = """
{
    "answers": [  # List of answer check results
        {
            "question_id": <int>,  # Return the question ID as well.
            "answer": "<string>",  # The user's answer
            "explanation": "<string>",  # Maximum 2 sentence explanation of the answer. if correct return empty string.
            "correct": <bool>  # Whether the answer is correct or not
        }
    ],
    "user_total_score": <float>  # The total score of the user (sum of correct answers)
}
"""

quiz_correction_input_schema = """
{
    "answer": "<string>",  # The answer given by the user
    "question": "<string>",  # A question to be answered
    "question_id": <int>,  # The ID of the question (DO NOT change this)
    "question_score": <int>  # The score of the question
}
"""