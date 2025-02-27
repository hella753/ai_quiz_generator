import json
from decouple import config
from django.utils.translation import gettext as _
from openai import OpenAI
from quiz_app.utils.validation_models.quiz_creation_schema import Quiz, creation_schema_str
from quiz_app.utils.validation_models.quiz_correction_schema import QuizAnswers, quiz_correction_input_schema, \
    quiz_correction_schema


class QuizGenerator:
    """
    This class is used to generate quiz questions and
    check answers using OpenAI API.
    """
    def __init__(self):
        self.__API_KEY = config('SECRET_KEY')
        self.__client = OpenAI(api_key=self.__API_KEY)

    def use_ai(self, sys_prompt: str, prompt: str):
        """
        Use the AI model to generate a response.
        """
        completion = self.__client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        try:
            response = completion.choices[0].message.content
            return response
        except json.JSONDecodeError:
            print("Validation error")
            return None
        except KeyError:
            print("Unexpected response format")
            return None

    def generate_quiz(self, prompt, file=None):
        """
        Generate a quiz using the AI model.
        """
        sys_prompt = _(f"Please generate a quiz based on the following schema: {creation_schema_str}."
                       f"If a question is open-ended, 'answers' should be an empty list. "
                       f"user_total_score field should be the sum of the questions score which are correct.")

        if file is not None:
            sys_prompt += f"Use this text for generating questions {file}"

        raw_response = self.use_ai(sys_prompt, prompt)
        if raw_response:
            try:
                data = Quiz(**json.loads(raw_response))  # Parse and validate quiz
                return data.model_dump() # Dump the model to a dictionary
            except ValueError:
                print("Quiz validation failed.")
                return None
        return None

    def check_answers(self, prompt):
        """
        Check the answers to a quiz using the AI model.
        """
        sys_prompt = _(f"You will be given a quiz with the following details for each question: "
                       f"{quiz_correction_input_schema}. You should return the result in the "
                       f"following JSON format: {quiz_correction_schema}. ")

        raw_response = self.use_ai(sys_prompt, prompt)
        if raw_response:
            try:
                data = QuizAnswers(**json.loads(raw_response))  # Parse and validate answers
                data = data.model_dump() # Dump the model to a dictionary
                return data
            except ValueError:
                print("Answer checking validation failed.")
                return None
        return None