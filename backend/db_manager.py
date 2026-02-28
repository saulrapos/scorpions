import chromadb
from chromadb.utils import embedding_functions

# 1. EL CAMBIO CLAVE: Usamos EphemeralClient para que la memoria sea temporal (en RAM)
chroma_client = chromadb.EphemeralClient()

# 2. Cargar el modelo GRATUITO recomendado
modelo_local = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Crear la colección temporal
collection = chroma_client.get_or_create_collection(
    name="documentos_hackathon",
    embedding_function=modelo_local
)

def add_documents_to_db(chunks, filename):
    """Guarda los trozos de texto en la memoria temporal."""
    if not chunks:
        return

    ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def search_documents(query, n_results=5):
    """Busca los fragmentos usando IA local"""
    # Si la colección está vacía (acabamos de arrancar), evitamos que dé error
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
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