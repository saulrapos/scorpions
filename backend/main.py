from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
from document_processor import extract_and_clean_pdf
from db_manager import add_documents_to_db, search_documents

app = FastAPI(title="Scorpions Nexus API", description="Buscador Inteligente con IA")

# Permitir que el HTML conecte con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

class SearchQuery(BaseModel):
    pregunta: str

@app.get("/")
def home():
    return {"mensaje": "API Scorpions Operativa 🚀"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Por ahora solo procesamos PDFs.")

    try:
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        chunks = extract_and_clean_pdf(file_path)
        add_documents_to_db(chunks, file.filename)

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search(query: SearchQuery):
    try:
        # Buscamos los 5 resultados más relevantes
        resultados = search_documents(query.pregunta, n_results=5)
        return {"resultados": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)