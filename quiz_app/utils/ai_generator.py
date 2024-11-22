import json
from decouple import config
from openai import OpenAI


class QuizGenerator:
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
        # print(response)
        data = json.loads(response)
        return data

    def generate_quiz(self, prompt, file=""):
        sys_prompt = ("return JSON object. structure: 'name', 'questions' "
                      "should have nested 'question', 'score': 1.00 "
                      "and 'answers' list. If quiz is multiple choice: "
                      "'answers' should have 'answer', 'correct': bool "
                      "If questions are open 'answers' should be an empty list. "
                      "Dont Write anything rather then just object. not even json "
                      "in the beginning. If user says that he needs more than 10 "
                      "questions dont generate anything.")
        if file != "":
            sys_prompt += f"Use this text for generating questions {file}"
        data = self.use_ai(sys_prompt, prompt)
        return data

    def check_answers(self, prompt):
        sys_prompt = ("You are an AI assistant that helps with checking quiz answers. "
                      "You'll be given questions, answers, and question_ids. DO NOT TOUCH THE QUESTION_ID! "
                      "Return the response in JSON format with fields: question_id, answer, explanation(short, only one sentence, max 2."
                      "If the answer is correct, leave the explanation field empty.), "
                      "and correct(True or False)."
                      "Dont Write anything rather then just object. not even json "
                      "in the beginning."
                      )
        return self.use_ai(sys_prompt, prompt)
