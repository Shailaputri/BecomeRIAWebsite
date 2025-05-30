import fitz  # PyMuPDF

def extract_content_from_pdf(pdf_path, max_pages=2):
    doc = fitz.open(pdf_path)
    content = ""
    for i in range(min(max_pages, len(doc))):
        content += doc[i].get_text()
    return content.strip()
