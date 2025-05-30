import datetime, os
from extract_pdf import extract_content_from_pdf
from llm_service import generate_mcqs_from_text, generate_news_mcqs_from_sebi_feed

TEMPLATE_PATH = "quiz_generator/templates/quiz_template.html"
PDF_PATH = "quiz_generator/input/source.pdf"
OUTPUT_FOLDER = "quiz_generator/output"

def render_html(mcqs, date_str):
    with open("quiz_generator/templates/base_quiz.html", "r", encoding="utf-8") as f:
        template = f.read()

    questions_html = ""
    for q in mcqs:
        options = "".join(f"<li>{opt}</li>" for opt in q["options"])
        questions_html += f'<div class="question"><p>{q["question"]}</p><ul>{options}</ul></div>'

    return template.replace("{{date}}", date_str).replace("{{questions}}", questions_html)

def save_html(html, file_name):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    filename = os.path.join(OUTPUT_FOLDER, f"{file_name}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

def main():
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")

    text = extract_content_from_pdf(PDF_PATH)
    # academic_qs = generate_mcqs_from_text(text, 3)
    academic_qs = [
            {
                "question": "What is the full form of SEBI?",
                "options": [
                    "A. Securities and Exchange Board of India",
                    "B. Stock Exchange Bureau of India",
                    "C. Securities Enforcement Board of India",
                    "D. Standard Economic Board of India"
                ],
                "answer": "A"
            }]
    # news_qs = generate_news_mcqs((today - datetime.timedelta(days=1)).isoformat(), 2)
    news_qs = generate_news_mcqs_from_sebi_feed(2)

    # if news_qs or academic_qs is None:
    if news_qs is None:
        # 🛑 News MCQ generation failed — render default fallback page
        with open("templates/default_template.html", "r", encoding="utf-8") as f:
            fallback_html = f.read()

        save_html(fallback_html, "latest_quiz.html")
        save_html(fallback_html, f"quiz_{date_str}.html")
        print("⚠️ Rendered fallback page due to LLM failure.")
        return

    all_qs = academic_qs + news_qs
    html = render_html(all_qs, date_str)
    save_html(html, f"quiz_{date_str}.html")
    save_html(html, "latest_quiz.html")


if __name__ == "__main__":
    main()
