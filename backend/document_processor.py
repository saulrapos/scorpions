import fitz  # PyMuPDF
import re
import csv
from docx import Document as DocxDocument

def clean_text(text: str) -> str:
    """Limpieza básica de espacios y saltos de línea."""
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_text(file_path: str) -> str:
    """Extrae el texto dependiendo del tipo de archivo."""
    ext = file_path.split('.')[-1].lower()
    text = ""

    try:
        if ext == 'pdf':
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text("text") + " "
        elif ext == 'docx':
            doc = DocxDocument(file_path)
            text = " ".join([para.text for para in doc.paragraphs])
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        elif ext == 'csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    text += " ".join(row) + " "
    except Exception as e:
        print(f"Error extrayendo texto de {file_path}: {e}")

    return clean_text(text)

def extract_and_clean_document(file_path: str):
    """Extrae, limpia y divide el documento en fragmentos por PALABRAS (no caracteres)."""
    text = extract_text(file_path)
    if not text:
        return []

    # Separamos todo el documento en una lista de palabras completas
    palabras = text.split()
    
    # Configuramos el tamaño en PALABRAS (200 palabras son aprox. 1 párrafo largo)
    chunk_size = 200 
    overlap = 50  # Solapamos 50 palabras para no cortar ideas entre fragmentos
    chunks = []
    
    # Bucle mejorado que no corta palabras por la mitad
    for i in range(0, len(palabras), chunk_size - overlap):
        # Cogemos un bloque de 200 palabras
        bloque_palabras = palabras[i:i + chunk_size]
        # Las volvemos a unir en un solo texto con espacios
        chunk = " ".join(bloque_palabras)
        
        if chunk.strip():
            chunks.append(chunk)
            
    return chunks