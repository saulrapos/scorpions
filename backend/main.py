from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from document_processor import extract_and_clean_pdf
from db_manager import add_documents_to_db, search_documents

app = FastAPI(title="Nexus API", description="MVP Buscador Documental Inteligente")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

# --- MODELOS DE DATOS ---
class SearchQuery(BaseModel):
    pregunta: str

# --- RUTAS ---
@app.get("/")
def home():
    return {"mensaje": "API del Hackathon operativa 🚀"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo aceptamos PDFs por ahora.")

    # 1. Guardar archivo temporal
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 2. Extraer y limpiar el texto
    chunks = extract_and_clean_pdf(file_path)

    # 3. Guardar en Base de Datos Vectorial (La IA local)
    add_documents_to_db(chunks, file.filename)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_indexados": len(chunks),
        "mensaje": "¡Documento procesado e indexado con IA!"
    }

@app.post("/api/search")
async def search(query: SearchQuery):
    # 4. Buscar documentos por significado
    resultados = search_documents(query.pregunta)

    return {
        "pregunta": query.pregunta,
        "resultados": resultados
    }