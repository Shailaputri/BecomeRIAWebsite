BASE_TEMPLATE_PATH = "quiz_generator/templates/base_quiz.html"

def render_html(mcqs, date_str):
    with open(BASE_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    questions_html = ""
    correct_answers_dict = {}

    for i, q in enumerate(mcqs, 1):
        qname = f"q{i}"
        correct_answers_dict[qname] = q["answer"].lower()

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

    html_output = template.replace("{{date}}", date_str)\
                          .replace("{{questions}}", questions_html)\
                          .replace("{{ correctAnswers | safe }}", json.dumps(correct_answers_dict))
    return html_output
