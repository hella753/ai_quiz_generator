import logging
from typing import Type
from decouple import config
from django.utils.translation import gettext as _
from openai import OpenAI
from pydantic import BaseModel

from quiz_app.exceptions import QuizGenerationError
from quiz_app.utils.pydantic_models import Quiz
from quiz_app.utils.pydantic_models import QuizAnswers

logger = logging.getLogger(__name__)


class QuizGenerator:
    """
    This class is used to generate quiz questions and
    check answers using OpenAI API.
    """
    def __init__(self):
        self.__API_KEY = config('OPEN_AI_SECRET_KEY')
        self.__client = OpenAI(api_key=self.__API_KEY)

    def use_ai(self, sys_prompt: str, prompt: str, response_format: Type[BaseModel]):
        """
        Use the AI model to generate a response.
        """
        try:
            completion = self.__client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_format,
                temperature=0.8,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise QuizGenerationError(f"Failed to generate content: {str(e)}")

    def generate_quiz(self, prompt, file=None):
        """
        Generate a quiz using the AI model.
        """
        sys_prompt = _("Please generate a quiz in the required format. Scores should be 1.00 by default."
                       "and if the question is open-ended the answers list should be empty.")

        if file is not None:
            sys_prompt += f"Use this text for generating questions {file}"

        try:
            raw_response = self.use_ai(sys_prompt, prompt, Quiz)

            if not raw_response:
                raise QuizGenerationError("Received empty response from AI")

            return raw_response.model_dump()

        except Exception as e:
            logger.error(f"Quiz generation error: {str(e)}", exc_info=True)
            raise QuizGenerationError(f"Failed to generate quiz: {str(e)}")

    def check_answers(self, prompt):
        """
        Check the answers to a quiz using the AI model.
        """
        sys_prompt = _("Evaluate quiz answers and return a JSON response.")

        try:
            raw_response = self.use_ai(sys_prompt, prompt, QuizAnswers)

            if not raw_response:
                raise QuizGenerationError("Received empty response from answer evaluation")

            return raw_response.model_dump()

        except Exception as e:
            logger.error(f"Answer checking error: {str(e)}", exc_info=True)
            raise QuizGenerationError(f"Failed to check answers: {str(e)}")