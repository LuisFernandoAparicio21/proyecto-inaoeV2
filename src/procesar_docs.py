"""Pipeline de procesamiento de documentos para el sistema RAG INAOE.

Este módulo implementa un pipeline ETL (Extract, Transform, Load) para procesar
documentos PDF, enriquecerlos con análisis NLP usando spaCy y HuggingFace,
y almacenarlos en una base de datos vectorial FAISS.

El procesamiento es incremental: solo procesa documentos nuevos o modificados
comparando timestamps con un registro JSON persistente.

Modules:
    spacy: Procesamiento de lenguaje natural y NER en español.
    transformers: Pipeline de NER especializado con BERT.
    langchain: Carga de PDFs, splitting de texto y FAISS.
    torch: Soporte GPU para inferencia de modelos.

Typical usage:
    $ cd src
    $ python procesar_docs.py

Attributes:
    RUTA_PROYECTO (Path): Ruta raíz del proyecto.
    DIR_DOCS (Path): Directorio con documentos PDF a procesar.
    DIR_DB_FAISS (Path): Directorio donde se guarda el índice FAISS.
    EMBEDDING_MODEL (str): Modelo de embeddings (all-MiniLM-L6-v2).
    SPACY_MODEL (str): Modelo spaCy para español (es_core_news_lg).

Author:
    Proyecto INAOE

Version:
    2.0.0 - Con enriquecimiento NLP dual (spaCy + BERT)
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import shutil

# Configurar variables de entorno para modo offline (comentado temporalmente)
# os.environ["HF_HUB_OFFLINE"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"

import spacy
from transformers import pipeline
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

def cargar_registro_archivos() -> Dict[str, float]:
    """Carga el registro de archivos procesados desde un archivo JSON.
    
    Lee el archivo `processed_files.json` que contiene un diccionario
    mapeando rutas de archivos a sus timestamps de última modificación.
    
    Args:
        None
    
    Returns:
        Dict[str, float]: Diccionario donde las claves son rutas absolutas
            de archivos PDF y los valores son timestamps Unix de la última
            vez que fueron procesados. Retorna diccionario vacío si el
            archivo no existe.
    
    Example:
        >>> registro = cargar_registro_archivos()
        >>> print(registro)
        {'C:/docs/paper.pdf': 1702857600.0}
    """
    if not ARCHIVO_REGISTRO.exists():
        return {}
    with open(ARCHIVO_REGISTRO, 'r') as f:
        return json.load(f)


def guardar_registro_archivos(registro: Dict[str, float]) -> None:
    """Guarda el registro actualizado de archivos procesados.
    
    Persiste el diccionario de archivos procesados en formato JSON
    para permitir procesamiento incremental en ejecuciones futuras.
    
    Args:
        registro (Dict[str, float]): Diccionario con rutas de archivos
            como claves y timestamps de modificación como valores.
    
    Returns:
        None
    
    Example:
        >>> registro = {'C:/docs/paper.pdf': 1702857600.0}
        >>> guardar_registro_archivos(registro)
    """
    with open(ARCHIVO_REGISTRO, 'w') as f:
        json.dump(registro, f, indent=4)

def obtener_archivos_a_procesar(registro: Dict[str, float]) -> List[str]:
    """Determina qué archivos PDF son nuevos o han sido modificados.
    
    Compara los timestamps de modificación de los archivos en el directorio
    de documentos con los almacenados en el registro para identificar
    archivos que necesitan ser procesados.
    
    Args:
        registro (Dict[str, float]): Diccionario con el registro actual de
            archivos procesados. Se modifica in-place añadiendo los nuevos
            archivos encontrados.
    
    Returns:
        List[str]: Lista de rutas absolutas a archivos PDF que necesitan
            ser procesados (nuevos o modificados desde la última ejecución).
    
    Side Effects:
        Modifica el diccionario `registro` añadiendo entradas para archivos
        nuevos o actualizando timestamps de archivos modificados.
    
    Example:
        >>> registro = {}
        >>> nuevos = obtener_archivos_a_procesar(registro)
        >>> print(len(nuevos))  # Número de PDFs en el directorio
    
    Note:
        Solo procesa archivos con extensión .pdf en el directorio DIR_DOCS.
    """
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

def procesar_lote_documentos(rutas_archivos: List[str]) -> List[Any]:
    """Carga y divide en chunks un lote de documentos PDF.
    
    Procesa cada archivo PDF usando PyPDFLoader y divide el contenido
    en chunks más pequeños usando RecursiveCharacterTextSplitter para
    optimizar la búsqueda semántica.
    
    Args:
        rutas_archivos (List[str]): Lista de rutas absolutas a archivos
            PDF a procesar.
    
    Returns:
        List[Any]: Lista de objetos Document de LangChain, cada uno
            representando un chunk de texto con sus metadatos (source, page).
    
    Raises:
        Los errores de carga individual se capturan y registran via logging,
        permitiendo que el procesamiento continúe con los demás archivos.
    
    Example:
        >>> chunks = procesar_lote_documentos(['doc1.pdf', 'doc2.pdf'])
        >>> print(len(chunks))  # Número total de chunks generados
    
    Note:
        Configuración del splitter:
        - chunk_size: 1000 caracteres
        - chunk_overlap: 200 caracteres (para mantener contexto)
    """
    documentos = []
    for ruta in rutas_archivos:
        try:
            loader = PyPDFLoader(ruta)
            documentos.extend(loader.load())
            logging.info(f"Cargado: {Path(ruta).name}")
        except Exception as e:
            logging.error(f"Error cargando el archivo {ruta}: {e}")
            continue
    
    if not documentos:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_documents(documentos)

# --- INICIO: SECCIÓN DE ENRIQUECIMIENTO (PASO 3) ---

@torch.no_grad()
def analizar_chunks_batch(
    chunks_texto: List[str],
    spacy_nlp: Any,
    hf_pipeline: Any
) -> List[Dict[str, Dict[str, List[str]]]]:
    """Analiza un lote de textos con spaCy y HuggingFace para extraer entidades.
    
    Implementa un pipeline de doble estación para enriquecer los chunks de texto
    con metadatos de Named Entity Recognition (NER) usando dos modelos
    complementarios: spaCy para NER general y BERT para NER especializado.
    
    El procesamiento en batch es significativamente más eficiente que procesar
    textos individualmente debido a la optimización de los modelos.
    
    Args:
        chunks_texto (List[str]): Lista de strings con el contenido de texto
            de cada chunk a analizar.
        spacy_nlp (Any): Modelo de spaCy cargado (ej: es_core_news_lg) con
            capacidades de NER.
        hf_pipeline (Any): Pipeline de HuggingFace configurado para NER
            (ej: bert-spanish-ner).
    
    Returns:
        List[Dict[str, Dict[str, List[str]]]]: Lista de diccionarios con metadatos
            por chunk. Cada diccionario contiene:
            - 'spacy_entities': Dict con entidades de spaCy agrupadas por tipo
            - 'hf_entities': Dict con entidades de BERT agrupadas por tipo
            
            Ejemplo de estructura:
            {
                'spacy_entities': {'ORG': ['INAOE'], 'PER': ['Juan']},
                'hf_entities': {'ORG': ['Instituto'], 'LOC': ['Puebla']}
            }
    
    Note:
        - El decorador @torch.no_grad() desactiva gradientes para ahorrar memoria.
        - Si HuggingFace falla, retorna listas vacías sin detener el proceso.
        - Tipos de entidades comunes: ORG, PER, LOC, MISC, DATE, NUM.
    
    Example:
        >>> chunks = ["El INAOE está en Puebla.", "Juan trabajó en el proyecto."]
        >>> metadatos = analizar_chunks_batch(chunks, nlp, hf_pipe)
        >>> print(metadatos[0]['spacy_entities'])
        {'ORG': ['INAOE'], 'LOC': ['Puebla']}
    """
    metadatos_enriquecidos = []

    # Estación 1: spaCy - nlp.pipe es la forma más rápida de procesar batch
    spacy_docs = list(spacy_nlp.pipe(chunks_texto))
    
    # Estación 2: HuggingFace - procesa automáticamente la lista
    try:
        hf_results = hf_pipeline(chunks_texto)
    except Exception as e:
        logging.error(f"Error en el pipeline de Hugging Face: {e}")
        hf_results = [[] for _ in chunks_texto]

    # Combinar resultados de ambas estaciones para cada chunk
    for i, doc in enumerate(spacy_docs):
        # Extraer entidades de spaCy agrupadas por tipo
        entidades_spacy: Dict[str, List[str]] = {}
        for ent in doc.ents:
            if ent.label_ not in entidades_spacy:
                entidades_spacy[ent.label_] = []
            entidades_spacy[ent.label_].append(ent.text)
        
        # Extraer entidades de HuggingFace agrupadas por tipo
        entidades_hf: Dict[str, List[str]] = {}
        for entity in hf_results[i]:
            label = entity.get('entity_group', 'MISC')
            if label not in entidades_hf:
                entidades_hf[label] = []
            entidades_hf[label].append(entity['word'])
        
        metadatos_enriquecidos.append({
            "spacy_entities": entidades_spacy,
            "hf_entities": entidades_hf
        })
        
    return metadatos_enriquecidos

# --- FIN: SECCIÓN DE ENRIQUECIMIENTO ---


# --- Flujo Principal ---

def main() -> None:
    """Flujo principal para procesar documentos de forma robusta e incremental.
    
    Ejecuta el pipeline completo de procesamiento de documentos:
    1. Carga modelos NLP (spaCy y HuggingFace)
    2. Detecta archivos nuevos/modificados
    3. Procesa y divide documentos en chunks
    4. Enriquece chunks con metadatos NER
    5. Actualiza la base de datos FAISS de forma atómica
    
    El proceso es incremental: solo procesa documentos nuevos o modificados
    desde la última ejecución, comparando timestamps almacenados en JSON.
    
    La actualización de la base de datos es atómica: primero guarda en un
    directorio temporal y luego reemplaza el directorio original, garantizando
    que si algo falla, la base de datos original permanece intacta.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        Los errores críticos se capturan y registran via logging.
        La base de datos original no se modifica si hay errores.
    
    Example:
        >>> # Desde línea de comandos:
        $ cd src
        $ python procesar_docs.py
        
        >>> # Desde código Python:
        >>> from procesar_docs import main
        >>> main()
    
    Note:
        Requisitos previos:
        - Modelo spaCy: python -m spacy download es_core_news_lg
        - Modelo BERT en: models/bert-spanish-ner/
        - PDFs en: documentos/
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