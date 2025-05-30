import os
import json
from extract_pdf import extract_content_from_pdf
from llm_service import generate_mcqs_from_text, generate_news_mcqs_from_sebi_feed
# from render import render_html
from datetime import date

APP_PATH="quiz_generator"
BASE_TEMPLATE_PATH = os.path.join(APP_PATH, "templates/base_quiz.html")
PDF_PATH = os.path.join(APP_PATH, "input/source.pdf")
OUTPUT_FOLDER = os.path.join(APP_PATH, "output")
QUESTION_BANK_PATH=os.path.join(APP_PATH, "question_bank/static_question_bank.json")
QUESTION_BANK_INDEX_PATH=os.path.join(APP_PATH, "question_bank/question_index_tracker.json")

def render_html_old(mcqs, date_str):
    with open(BASE_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    questions_html = ""
    correct_answers_js = "const correctAnswers = {\n"

    for i, q in enumerate(mcqs, 1):
        qname = f"q{i}"
        correct_option = q["answer"].lower()
        correct_answers_js += f'  "{qname}": "{correct_option}",\n'

        options_html = ""
        for j, opt in enumerate(q["options"]):
            letter = ["a", "b", "c", "d"][j]
            options_html += f'<label class="option"><input type="radio" name="{qname}" value="{letter}"> {opt}</label>\n'

        questions_html += f"""
        <div class="question">
          <div class="card question-content">
            <h4>{i}. {q["question"]}</h4>
            {options_html}
          </div>
        </div>
        """

    correct_answers_js += "};"

    return (
        template
        .replace("{{date}}", date_str)
        .replace("{{questions}}", questions_html)
        .replace("const correctAnswers = {{ correctAnswers | safe }};", correct_answers_js)
    )

def render_html(mcqs, date_str):
    with open(BASE_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    questions_html = ""
    correct_answers_dict = {}

    answer_review = []
    for i, q in enumerate(mcqs, 1):
        qname = f"q{i}"
        correct_answers_dict[qname] = q["answer"].lower()

        options_html = ""
        for j, opt in enumerate(q["options"]):
            letter = ["a", "b", "c", "d"][j]
            options_html += f'<label class="option"><input type="radio" name="{qname}" value="{letter}"> {opt}</label>\n'

        # Save full question and correct answer text for review section
        answer_letter = q["answer"].strip().lower()[0]  # get 'a', 'b', etc.
        correct_option_index = ["a", "b", "c", "d"].index(answer_letter)
        correct_option_text = q["options"][correct_option_index]
        answer_review.append({
            "question": q["question"],
            "answer": f"{correct_option_text}"
        })

        questions_html += f"""
        <div class="question">
          <div class="card question-content">
            <h4>{i}. {q["question"]}</h4>
            {options_html}
          </div>
        </div>
        """

    html_output = template\
        .replace("{{date}}", date_str)\
        .replace("{{questions}}", questions_html)\
        .replace("{{ correctAnswers | safe }}", json.dumps(correct_answers_dict))\
        .replace("{{ answerReview | safe }}", json.dumps(answer_review))

    return html_output


def save_html(html, file_name):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    filename = os.path.join(OUTPUT_FOLDER, f"{file_name}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename


def get_next_static_questions(bank_path=QUESTION_BANK_PATH,
                               index_path=QUESTION_BANK_INDEX_PATH):
    with open(bank_path, "r") as f:
        question_bank = json.load(f)

    with open(index_path, "r") as f:
        tracker = json.load(f)

    selected_questions = []

    for topic in question_bank:
        index = tracker.get(topic, 0)
        questions = question_bank[topic]

        if not questions:
            continue

        selected_questions.append(questions[index])
        tracker[topic] = (index + 1) % len(questions)  # wrap around when done

    with open(index_path, "w") as f:
        json.dump(tracker, f, indent=2)

    return selected_questions

def main():
    today = date.today()
    date_str = today.strftime("%Y-%m-%d")

    static_qs = get_next_static_questions()
    dynamic_qs = generate_news_mcqs_from_sebi_feed()

    if dynamic_qs is None:
        print("⚠️ Using only static questions due to LLM failure.")
        all_qs = static_qs
    else:
        all_qs = static_qs + dynamic_qs

    html = render_html(all_qs, date_str)
    save_html(html, f"quiz_{date_str}.html")
    save_html(html, "latest_quiz.html")
    print(f"✅ Quiz generated for {date_str}")


if __name__ == "__main__":
    main()
