import os
import chromadb
from chromadb.utils import embedding_functions

# 1. Iniciar ChromaDB en local
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# 2. Cargar el modelo GRATUITO recomendado por Merlin Software
# La primera vez que ejecutes esto, tardará un poco porque descargará el modelo (~80MB)
modelo_local = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Crear o cargar la colección usando el modelo local
collection = chroma_client.get_or_create_collection(
    name="documentos_hackathon",
    embedding_function=modelo_local
)

def add_documents_to_db(chunks, filename):
    """Guarda los trozos de texto. ChromaDB generará los vectores automáticamente."""
    if not chunks:
        return

    ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]

    # Al pasarle los documentos, Chroma usa el modelo local para vectorizarlos
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def search_documents(query, n_results=3):
    """Busca los fragmentos usando IA local"""
    results = collection.query(
        query_texts=[query], # Le pasamos el texto directamente
        n_results=n_results
    )

    # Formatear la respuesta para el Frontend
    documentos_encontrados = []
    if results['documents']:
        for i in range(len(results['documents'][0])):
            documentos_encontrados.append({
                "texto": results['documents'][0][i],
                "archivo": results['metadatas'][0][i]['filename'],
                "distancia": results['distances'][0][i] if 'distances' in results else 0
            })

    return documentos_encontrados