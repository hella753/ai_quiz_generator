import json
from decouple import config
from openai import OpenAI


class QuizGenerator:
    def __init__(self, prompt):
        self.API_KEY = config('SECRET_KEY')
        self.client = OpenAI(api_key=self.API_KEY)
        self.prompt = prompt
        self.SYS_PROMPT = ("return JSON object. structure: 'name', 'questions' "
                           "should have nested 'question', 'score': 1.00 "
                           "and 'answers' list. If quiz is multiple choice: "
                           "'answers' should have 'answer', 'correct': bool "
                           "If questions are open 'answers' should be an empty list. "
                           "Dont Write anything rather then just object. not even json "
                           "in the beginning. If user says that he needs more than 10 "
                           "questions dont generate anything.")

    def generate_quiz(self, file=""):
        sys_prompt = self.SYS_PROMPT
        if file != "":
             sys_prompt += f"Use this text for generating questions {file}"
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": self.prompt}
            ],
            response_format={"type": "json_object"}
        )
        response = completion.choices[0].message.content
        data = json.loads(response)
        return data

    def check_answers(self):
        pass