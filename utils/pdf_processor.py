import fitz  # PyMuPDF for PDF extraction

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file.
    :param pdf_file: The uploaded PDF file object
    :return: Extracted text as a string
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text