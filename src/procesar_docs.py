# procesar_docs_v2.py
#Enriquesimiento con spcay NLU y Huggin Face 

import os
import json
import logging
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import shutil

# Configurar variables de entorno para modo offline (comentado temporalmente)
# os.environ["HF_HUB_OFFLINE"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"

#Actualizacion 2: Modelo Enriquecido con Spacy y Transformers
import spacy #procesamiento de lenguaje natural
from transformers import pipeline # modelo pre-entrenado ("ner" o Reconocimiento de Entidades Nombradas)
import torch 

# --- Configuración Centralizada ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Usar pathlib para un manejo de rutas robusto y legible
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
DIR_DOCS = RUTA_PROYECTO / "documentos"

#Rutas del proyecto
DIR_DB_FAISS = RUTA_PROYECTO / "indice_faiss"
DIR_DB_TEMP = RUTA_PROYECTO / "indice_faiss_temp"
ARCHIVO_REGISTRO = RUTA_PROYECTO / "processed_files.json"

#MODELOS PARA ENRIQUECIMIENTO
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL= "es_core_news_lg" #Modelo de lenguaje pre-entrando

# Cambiamos el nombre del modelo por una ruta a la carpeta local que creaste
RUTA_MODELO_HF = RUTA_PROYECTO / "models" / "bert-spanish-ner"

# --- Funciones De Procesamiento---

def cargar_registro_archivos():
    """Carga el registro de archivos procesados desde un JSON."""
    if not ARCHIVO_REGISTRO.exists():
        return {}
    with open(ARCHIVO_REGISTRO, 'r') as f:
        return json.load(f)

def guardar_registro_archivos(registro):
    """Guarda el registro actualizado de archivos procesados."""
    with open(ARCHIVO_REGISTRO, 'w') as f:
        json.dump(registro, f, indent=4)

def obtener_archivos_a_procesar(registro):
    """Determina qué archivos son nuevos o han sido modificados."""
    archivos_nuevos = []
    if not DIR_DOCS.exists():
        logging.error(f"El directorio de documentos '{DIR_DOCS}' no existe.")
        return []
        
    for archivo_pdf in DIR_DOCS.glob("*.pdf"):
        nombre_archivo = str(archivo_pdf)
        ultima_modificacion = os.path.getmtime(nombre_archivo)
        
        if nombre_archivo not in registro or registro[nombre_archivo] < ultima_modificacion:
            archivos_nuevos.append(nombre_archivo)
            registro[nombre_archivo] = ultima_modificacion
            
    return archivos_nuevos

def procesar_lote_documentos(rutas_archivos):
    """Carga y divide en chunks un lote de documentos PDF."""
    documentos = []
    for ruta in rutas_archivos:
        try:
            loader = PyPDFLoader(ruta)
            documentos.extend(loader.load())
            logging.info(f"Cargado: {Path(ruta).name}")
        except Exception as e:
            logging.error(f"Error cargando el archivo {ruta}: {e}")
            continue # Salta al siguiente archivo si uno falla
    
    if not documentos:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_documents(documentos)

# --- INICIO: SECCIÓN DE ENRIQUECIMIENTO (PASO 3) ---

@torch.no_grad() # Decorador: Desactiva el cálculo de gradientes solo vamos a usar los modelos para predecir, no para entrenar
def analizar_chunks_batch(chunks_texto, spacy_nlp, hf_pipeline):
    """
    Analiza un lote ('batch') de textos con spaCy y Hugging Face.
    Procesar en lotes es mucho más eficiente que hacerlo uno por uno.
    """
    metadatos_enriquecidos = []

    # --- Estación 1: spaCy ---
    # nlp.pipe es la forma más rápida de procesar múltiples textos con spaCy.
    spacy_docs = list(spacy_nlp.pipe(chunks_texto))
    
    # --- Estación 2: Hugging Face ---
    # El pipeline de HF procesa automáticamente la lista de textos.
    try:
        hf_results = hf_pipeline(chunks_texto)
    except Exception as e:
        logging.error(f"Error en el pipeline de Hugging Face: {e}")
        # Si HF falla, creamos una lista vacía para que el proceso no se detenga.
        hf_results = [[] for _ in chunks_texto]

    # Ahora combinamos los resultados de ambas estaciones para cada chunk
    for i, doc in enumerate(spacy_docs):
        # Procesar resultados de spaCy: se extraen las entidades y se agrupan por etiqueta (ORG, PER, etc.)
        entidades_spacy = {}
        for ent in doc.ents:
            if ent.label_ not in entidades_spacy:
                entidades_spacy[ent.label_] = []
            entidades_spacy[ent.label_].append(ent.text)
        
        # Procesar resultados de Hugging Face: similar a spaCy, se agrupan por etiqueta.
        entidades_hf = {}
        # hf_results es una lista de listas (una lista de entidades por cada texto del lote).
        for entity in hf_results[i]:
            # entity_group es la etiqueta que asigna el modelo (ej: 'PER', 'ORG').
            label = entity.get('entity_group', 'MISC')
            if label not in entidades_hf:
                entidades_hf[label] = []
            # 'word' es el texto de la entidad que el modelo encontró.
            entidades_hf[label].append(entity['word'])
        
        # Guardamos los metadatos de este chunk en nuestra lista final
        metadatos_enriquecidos.append({
            "spacy_entities": entidades_spacy,
            "hf_entities": entidades_hf
        })
        
    return metadatos_enriquecidos

# --- FIN: SECCIÓN DE ENRIQUECIMIENTO ---


# --- Flujo Principal ---

def main():
    """
    Flujo principal para procesar documentos de forma robusta e incremental.
    """
    logging.info("🚀 Iniciando proceso de actualización de la base de datos vectorial.")

    # --- 1. Cargar los modelos de NLU al principio ---
    #Natural Language Understanding, permite  comprender e interpretar el lenguaje humano, procesamiento de palabras.
    logging.info(f"Cargando modelo de spaCy: {SPACY_MODEL}")
    try:
        spacy_nlp = spacy.load(SPACY_MODEL)
    except OSError:
        logging.error(f"Modelo de spaCy '{SPACY_MODEL}' NO ENCONTRADO. Ejecuta: python -m spacy download {SPACY_MODEL}" )
        return 

    
    # Eliminamos el token y cargamos el modelo desde la ruta local
    logging.info(f"Cargando modelo NER local desde: {RUTA_MODELO_HF}")

    # Verificamos si la carpeta del modelo existe para evitar errores
    if not RUTA_MODELO_HF.exists():
        logging.error(f"La carpeta del modelo no se encontró en: {RUTA_MODELO_HF}")
        logging.error("Asegúrate de haber descargado los archivos del modelo en la carpeta /models.")
        return

    # torch.cuda.is_available() comprueba si tienes una GPU compatible con NVIDIA.
    device = 0 if torch.cuda.is_available() else -1 
    
    hf_pipeline = pipeline(
        "ner",
        model=str(RUTA_MODELO_HF),      # Usamos la ruta local
        tokenizer=str(RUTA_MODELO_HF),  # Usamos la ruta local
        device=device,
        grouped_entities=True
    )
    




    ## --- 2. Determinar que documentos procesar --- 
    registro_archivos = cargar_registro_archivos()
    archivos_a_procesar = obtener_archivos_a_procesar(registro_archivos)
    
    if not archivos_a_procesar and DIR_DB_FAISS.exists():
        logging.info("✅ No hay documentos nuevos o modificados. La base de datos está actualizada.")
        return

    try:
        # --- 3. Cargar y dividir los nuevos documentos ---
        logging.info(f"Se encontraron {len(archivos_a_procesar)} archivos para procesar.")
        chunks_nuevos = procesar_lote_documentos(archivos_a_procesar)
        
        if not chunks_nuevos:
            logging.warning("No se generaron chinks a partir de los documentos, Finalizando la carga")
            return

        # --- 4. Enriquecer los nuecos chunks con la "linea de ensamblaje"
        logging.info(f"Enriqueciendo {len (chunks_nuevos)} nuevos chunks con metadatos de NLU....")
        textos_de_chunks = [chunk.page_content for chunk in chunks_nuevos]
        
        #Se llama a la funcionn que se creo para el analisis 
        metadatos_enriquecidos = analizar_chunks_batch(textos_de_chunks, spacy_nlp, hf_pipeline)

        #añaden los metadatos generados a cada chunk
        for i, chunk in enumerate(chunks_nuevos):
            chunk.metadata.update(metadatos_enriquecidos[i])

        logging.info("Capa de filtro inteligente: Enriquecimiento completado")

        # --- 5 ACTUALIZAR BASE DE DATOS VECTORIAL
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            cache_folder=str(RUTA_PROYECTO / "models")  # Usar carpeta local para cache
        )
        

        #CONTEXTO DEL DIRECTORIO VECTORIAL
        # paso 1 Eliminar el directorio temporal si existe de una ejecución anterior fallida
        if DIR_DB_TEMP.exists():
            shutil.rmtree(DIR_DB_TEMP)

        # Paso 2: Cargar la base de datos existente o crear una nueva
        if DIR_DB_FAISS.exists() and chunks_nuevos:
            logging.info("Cargando base de datos existente para fusionar...")
            db_existente = FAISS.load_local(str(DIR_DB_FAISS), embeddings, allow_dangerous_deserialization=True)
            db_existente.add_documents(chunks_nuevos)
            db_final = db_existente
        elif chunks_nuevos:
            logging.info("Creando una nueva base de datos vectorial...")
            db_final = FAISS.from_documents(chunks_nuevos, embeddings)
        else:
            logging.info("No hay chunks para procesar. Finalizando.")
            return

        # Paso 3: Guardar en un directorio temporal (Principio de Atomicidad)
        logging.info(f"Guardando índice actualizado en directorio temporal: {DIR_DB_TEMP}")
        db_final.save_local(str(DIR_DB_TEMP))
        
        # Paso 4: Reemplazo Atómico
        # Si todo fue exitoso, eliminamos el directorio antiguo y renombramos el nuevo.
        logging.info("Reemplazando la base de datos antigua con la nueva versión...")
        if DIR_DB_FAISS.exists():
            shutil.rmtree(DIR_DB_FAISS)
        os.rename(DIR_DB_TEMP, DIR_DB_FAISS)
        
        # Paso 5: Actualizar el registro de archivos procesados
        guardar_registro_archivos(registro_archivos)
        
        logging.info(f"🎉 ¡Proceso completado! Base de datos guardada en: {DIR_DB_FAISS}")

    except Exception as e:
        logging.error(f"❌ Ocurrió un error crítico durante el proceso: {e}")
        logging.info("La operación fue abortada. La base de datos original no ha sido modificada.")
        # Limpiar el directorio temporal en caso de error
        if DIR_DB_TEMP.exists():
            shutil.rmtree(DIR_DB_TEMP)
            
if __name__ == "__main__":
    main()