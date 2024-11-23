import json
from decouple import config
from openai import OpenAI
from django.utils.translation import gettext as _


class QuizGenerator:
    """
    This class is used to generate quiz questions and
    check answers using OpenAI API.
    """

    def __init__(self):
        self.__API_KEY = config('SECRET_KEY')
        self.__client = OpenAI(api_key=self.__API_KEY)

    def use_ai(self, sys_prompt, prompt):
        completion = self.__client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        response = completion.choices[0].message.content
        data = json.loads(response)
        return data

    def generate_quiz(self, prompt, file=None):
        sys_prompt = _("return JSON object. structure: 'name', 'questions' "
                       "should have nested 'question', 'score': 1.00 "
                       "and 'answers' list. If quiz is multiple choice: "
                       "'answers' should have 'answer', 'correct': bool "
                       "If questions are open 'answers' should be "
                       "an empty list. Dont Write anything rather then "
                       "just object. not even json in the beginning. "
                       "If user says that he needs more than 10 "
                       "questions dont generate anything.")
        if file is not None:
            sys_prompt += f"Use this text for generating questions {file}"
        data = self.use_ai(sys_prompt, prompt)
        return data

    def check_answers(self, prompt):
        sys_prompt = _("Checking quiz answers. You'll be given questions, answers, "
                       "question_id and question_score. DO NOT TOUCH THE QUESTION_ID! "
                       "Return the response in JSON format with fields: \"answers\" "
                       "field which will have these nested "
                       "fields: question_id, answer, explanation(short, only one sentence, "
                       "max 2. If the answer is correct, leave the explanation field empty.), "
                       "and correct(True or False). After the answers field, I also want a "
                       "user_total_score field which should be the sum of the "
                       "questions score which are correct. Dont Write anything rather "
                       "then just object. not even json in the beginning.")
        return self.use_ai(sys_prompt, prompt)
