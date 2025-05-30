import json
import os
from extract_pdf import extract_content_from_pdf
from llm_service import generate_mcqs_for_topic, get_llm_response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to mcq_generator.py
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # one level up
BASE_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "quiz_generator", "templates", "base_quiz.html")
PDF_PATH = os.path.join(PROJECT_ROOT, "quiz_generator", "input", "source.pdf")
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "quiz_generator")
QUESTION_BANK_PATH=os.path.join(PROJECT_ROOT, "quiz_generator", "question_bank", "static_question_bank.json")
QUESTION_BANK_INDEX_PATH=os.path.join(PROJECT_ROOT, "quiz_generator", "question_bank", "question_index_tracker.json")

def build_question_bank(pdf_path=PDF_PATH):
    print("📘 Extracting PDF content...")
    full_text = extract_content_from_pdf(pdf_path, max_pages=10)

    print("📚 Asking LLM to suggest 3 topics...")
    topics_prompt = f"""
    Divide the content below into 3 meaningful financial education topics.
    Respond in format: ["Topic A", "Topic B", "Topic C"]

    TEXT:
    {full_text}
    """
    topics = get_llm_response(topics_prompt)  # This should return a list of strings
    if not isinstance(topics, list) or len(topics) != 3:
        raise ValueError("LLM did not return exactly 3 topics")

    print(f"✅ Topics identified: {topics}")
    question_bank = {}
    tracker = {}

    for topic in topics:
        print(f"🧠 Generating MCQs for: {topic}")
        topic_questions = generate_mcqs_for_topic(full_text, topic, n=33)
        question_bank[topic] = topic_questions
        tracker[topic] = 0

    os.makedirs("question_bank", exist_ok=True)

    with open(QUESTION_BANK_PATH, "w") as f:
        json.dump(question_bank, f, indent=2)
    with open(QUESTION_BANK_INDEX_PATH, "w") as f:
        json.dump(tracker, f, indent=2)

    print("✅ Question bank and index tracker saved.")

if __name__ == "__main__":
    build_question_bank()
