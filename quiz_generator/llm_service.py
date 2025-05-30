from openai import OpenAI
import datetime
import os
from openai import OpenAIError
from dotenv import load_dotenv
from news_fetcher import fetch_latest_sebi_news

load_dotenv()

open_ai_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=open_ai_key)
def safe_eval_mcqs(response_text):
    try:
        # Only try eval if response starts with [ and ends with ]
        if response_text.strip().startswith("[") and response_text.strip().endswith("]"):
            return eval(response_text)
    except Exception as e:
        print("⚠️ Eval failed:", e)
    return []  # return empty list if invalid

def generate_mcqs_from_text(text, n_questions=3):
    prompt = f"""
    Create {n_questions} MCQs from the academic text below.
    Each MCQ should have four options (A to D) and the correct answer.
    Format:
    [
      {{
        "question": "...",
        "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
        "answer": "B"
      }},
      ...
    ]

    TEXT:
    {text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return eval(response.choices[0].message.content)
    except OpenAIError as e:
            print("⚠️ OpenAI API failed:", e)
            return None
def generate_news_mcqs_from_sebi_feed(n_questions=2):
    news_summary = fetch_latest_sebi_news()

    prompt = f"""
You are a quiz master. Based on the following news articles related to SEBI and investments in India, generate {n_questions} multiple choice questions.

Each question must have:
- 4 options (A to D)
- 1 correct answer

News Articles:
{news_summary}

Format:
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A"
  }},
  ...
]
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        return safe_eval_mcqs(response.choices[0].message.content)
    except OpenAIError as e:
        print("⚠️ OpenAI API failed:", e)
        return None


# def generate_news_mcqs(date_string, n_questions=2):
#     prompt = f"""
#     Generate {n_questions} current affairs MCQs from the global news of {date_string}.
#     Format:
#     [
#       {{
#         "question": "...",
#         "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
#         "answer": "C"
#       }},
#       ...
#     ]
#     """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7,
#         )
#         return eval(response.choices[0].message.content)
#     except OpenAIError:
#         return templates/default_template.html
