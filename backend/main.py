from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
from document_processor import extract_and_clean_document
from db_manager import add_documents_to_db, search_documents

app = FastAPI(title="Scorpions Nexus API", description="Buscador Inteligente con IA")

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
    # 1. Nos quedamos SOLO con el nombre del archivo, ignorando la ruta de la carpeta
    filename_only = os.path.basename(file.filename)
    ext = filename_only.split('.')[-1].lower()
    formatos_permitidos = ['pdf', 'docx', 'txt', 'csv']
    
    if ext not in formatos_permitidos:
        raise HTTPException(status_code=400, detail=f"El formato .{ext} no está soportado.")

    try:
        file_path = f"uploads/{filename_only}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        chunks = extract_and_clean_document(file_path)
        add_documents_to_db(chunks, filename_only)

        return {
            "status": "success",
            "filename": filename_only,
            "chunks": len(chunks)
        }
    except Exception as e:
        # 2. Imprimimos el error en la consola para saber exactamente qué falla
        print(f"❌ Error crítico procesando {filename_only}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search(query: SearchQuery):
    try:
        resultados = search_documents(query.pregunta, n_results=5)
        return {"resultados": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)