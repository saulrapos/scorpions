import os
import requests
import time

# Configuración
DATASET_DIR = "dataset" # La carpeta donde has guardado los PDFs de Merlin Software
API_URL = "http://127.0.0.1:8000"

def poblar_y_probar():
    print("🚀 Iniciando Test de Integración con el Dataset...\n")

    # Comprobar que el servidor está encendido
    try:
        requests.get(API_URL)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: El servidor no está encendido. Ejecuta primero 'python -m uvicorn main:app --reload'")
        return

    # 1. SUBIR TODOS LOS ARCHIVOS DEL DATASET
    archivos_subidos = 0
    if not os.path.exists(DATASET_DIR):
        print(f"❌ ERROR: No se encuentra la carpeta '{DATASET_DIR}'. Créala y mete los PDFs dentro.")
        return

    pdfs = [f for f in os.listdir(DATASET_DIR) if f.endswith('.pdf')]
    print(f"📂 Encontrados {len(pdfs)} PDFs en la carpeta '{DATASET_DIR}'. Procediendo a subir e indexar...\n")

    for filename in pdfs:
        ruta_pdf = os.path.join(DATASET_DIR, filename)
        print(f"⏳ Subiendo e indexando: {filename}...")

        with open(ruta_pdf, "rb") as f:
            # Enviamos el archivo al endpoint de subida
            respuesta = requests.post(f"{API_URL}/api/upload", files={"file": f})

            if respuesta.status_code == 200:
                datos = respuesta.json()
                print(f"   ✅ Éxito! Chunks generados: {datos.get('chunks_indexados')}")
                archivos_subidos += 1
            else:
                print(f"   ❌ Error al subir {filename}: {respuesta.text}")

    print(f"\n🎉 Fase 1 completada: {archivos_subidos}/{len(pdfs)} archivos subidos e indexados correctamente.\n")
    time.sleep(1) # Pequeña pausa dramática

    # 2. PROBAR LA BÚSQUEDA SEMÁNTICA
    # Puedes cambiar esta pregunta por algo que sepas que está en los PDFs
    pregunta_test = "¿Cuáles son las condiciones o requisitos principales?"

    print(f"🔍 Fase 2: Probando el motor de búsqueda semántica...")
    print(f"❓ Pregunta: '{pregunta_test}'")

    respuesta_busqueda = requests.post(f"{API_URL}/api/search", json={"pregunta": pregunta_test})

    if respuesta_busqueda.status_code == 200:
        resultados = respuesta_busqueda.json().get("resultados", [])
        print(f"\n✅ Búsqueda exitosa. Se encontraron {len(resultados)} fragmentos relevantes:\n")

        for i, res in enumerate(resultados, 1):
            print(f"--- RESULTADO {i} ---")
            print(f"📄 Archivo origen: {res['archivo']}")
            print(f"🎯 Relevancia (Distancia): {res['distancia']:.4f}")
            print(f"📝 Texto: {res['texto'][:200]}...\n") # Mostramos solo los primeros 200 caracteres
    else:
        print(f"❌ Error en la búsqueda: {respuesta_busqueda.text}")

if __name__ == "__main__":
    poblar_y_probar()