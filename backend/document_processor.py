import fitz  # PyMuPDF
import re

def extract_and_clean_pdf(file_path: str):
    text_chunks = []
    doc = fitz.open(file_path)

    for page in doc:
        text = page.get_text("text")

        # Limpieza básica
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        text = text.strip()

        if not text:
            continue

        # Chunking: Dividimos en bloques de ~1000 caracteres
        chunk_size = 1000
        for i in range(0, len(text), chunk_size):
            text_chunks.append(text[i:i+chunk_size])

    return text_chunks