import logging

from typing import Type, Optional, Dict
from decouple import config  # type: ignore
from openai import OpenAI
from pydantic import BaseModel

from exceptions.custom_exceptions import QuizGenerationError
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

    def use_ai(self,
               sys_prompt: str,
               prompt: str,
               response_format: Type[BaseModel]) -> Optional[BaseModel]:
        """
        Use the AI model to generate a response.

        :param sys_prompt: System prompt for the AI model.
        :param prompt: User prompt for the AI model.
        :param response_format: Pydantic model to parse the response.

        :return: Parsed response from the AI model.

        :raises QuizGenerationError: If the AI model fails to generate content.
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

    def generate_quiz(self,
                      prompt: str,
                      language:str,
                      file: Optional[str] = None) -> Dict:
        """
        Generate a quiz using the AI model.

        :param prompt: User prompt for the AI model.
        :param language: Language for the quiz questions.
        :param file: File to use for generating questions.

        :return: Parsed response from the AI model.

        :raises QuizGenerationError: If the AI model fails to generate content.
        """
        sys_prompt = (f"Please generate a quiz in the required format."
                      f"Scores should be 1.00 by default. "
                      f"if the question is open-ended, "
                      f"the answers list should be empty."
                      f"Language should be {language}")

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

    def check_answers(self, exp_language: str, prompt: str) -> Dict:
        """
        Check the answers to a quiz using the AI model.

        :param exp_language: Language for the explanation field.
        :param prompt: User prompt for the AI model.

        :return: Parsed response from the AI model.

        :raises QuizGenerationError: If the AI model fails to generate content.
        """
        sys_prompt = (f"Evaluate quiz answers and return a JSON response. "
                      f"If the answer is correct,"
                      f"leave the explanation field empty string. "
                      f"Note that question should be returned just as an ID. "
                      f"Explanation should be in this language: {exp_language}")

        try:
            raw_response = self.use_ai(sys_prompt, prompt, QuizAnswers)

            if not raw_response:
                raise QuizGenerationError(
                    "Received empty response from answer evaluation"
                )

            return raw_response.model_dump()

        except Exception as e:
            logger.error(f"Answer checking error: {str(e)}", exc_info=True)
            raise QuizGenerationError(f"Failed to check answers: {str(e)}")
