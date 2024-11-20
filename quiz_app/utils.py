import json
from openai import OpenAI
from decouple import config

API_KEY = config('SECRET_KEY')

client = OpenAI(api_key=API_KEY)


def generate_quiz(prompt):
    SYS_PROMPT = ("return JSON object. structure: 'name', 'questions' should have nested 'question' and 'answers' "
                  "list. If quiz is multiple choice: 'answers' should have 'answer', 'correct': bool, 'score': 1.00 "
                  "or 0.00. If questions are open 'answers' should be an empty list. Dont Write anything rather then "
                  "just object. not even json in the beginning")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )
    response = completion.choices[0].message.content
    data = json.loads(response)
    return data
