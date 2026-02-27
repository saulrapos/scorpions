from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from document_processor import extract_and_clean_pdf

app = FastAPI(title="Nexus API", description="MVP Buscador Documental Inteligente")

# Permisos para el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear carpeta temporal si no existe
os.makedirs("uploads", exist_ok=True)

@app.get("/")
def home():
    return {"mensaje": "API del Hackathon operativa 🚀"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo aceptamos PDFs mágicos por ahora.")

    # 1. Guardar el PDF temporalmente
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 2. Extraer y limpiar el texto
    chunks = extract_and_clean_pdf(file_path)

    # TODO: Aquí meteremos la base de datos vectorial luego

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_generados": len(chunks),
        "mensaje": "¡Documento procesado con éxito!"
    }