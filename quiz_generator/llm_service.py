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
    You are a quiz master. Based on the following news articles related to SEBI and investments in India, generate {n_questions} multiple choice questions that test core concepts relevant for the NISM exam and knowledge of latest developments in the field.

    Most importantly focus on evaluating a learner's understanding of:
    - Portfolio management
    - Investment instruments and strategies
    - Financial planning principles
    - Wealth management frameworks
    - Wealth creation strategies and regulatory updates

    Each question must:
    - Be based on or inspired by distinct article contents
    - Include 4 options (A to D)
    - Include only 1 correct answer

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
        ]"""
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

def get_llm_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return eval(response.choices[0].message.content)
    except Exception as e:
        print("⚠️ Topic generation failed:", e)
        return []

def generate_mcqs_for_topic(topic_text, topic_name, n):
    prompt = f"""
    You are a certified NISM-XA quiz master. 
    Generate **exactly {n}**  high-quality multiple choice questions (MCQs) relevant to aspirants preparing to become SEBI-registered financial advisors based on topic \"{topic_name}\" and from the textbook mentioned below.
    ⚠️ IMPORTANT: You must generate **EXACTLY {n} questions**. Do not stop early. Do not generate fewer.
    Focus on creating a **variety of question types**, including:
    - **"What" questions** (definitions, facts, concepts)
    - **"Why" questions** (reasons, implications)
    - **"How" questions** (processes, methods)
    - **"Where/When" questions** (contextual, regulatory timelines or locations)
    - Scenario-based application questions that test practical decision-making
    - **must not** keep questions like what is the purpose/passing marks etc that tests knowledge about conduct of NISM-Series-X-A: Investment Adviser (Level 1) Certification Examination.
    
    Each question must:
    - Check the conceptual clarity of the topic_name. 
    - Include 4 options (A to D) 
    - Keep only 20% of questions where D.All of the above is the answer. 
    - Include only 1 correct answer

    Use the context below to generate meaningful, exam-relevant MCQs.

    Textbook:
    {topic_text}
    
    Return only the output in this format:
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
            max_tokens = 3000,
        )
        return safe_eval_mcqs(response.choices[0].message.content)
    except Exception as e:
        print(f"⚠️ Failed to generate MCQs for topic '{topic_name}':", e)
        return []


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
