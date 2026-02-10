Arquitectura del Sistema
========================

Vision General
--------------

El Asistente INAOE implementa una arquitectura RAG (Retrieval-Augmented Generation) que combina busqueda semantica con generacion de lenguaje natural.

Descripcion de la Arquitectura
------------------------------

El sistema se compone de los siguientes elementos conectados en secuencia:

1. **USUARIO**: Interactua con el sistema a traves de la interfaz web.

2. **Streamlit UI (app.py)**: Interfaz web que recibe las consultas del usuario.

3. **Tres componentes de procesamiento**:
   - FAISS Retriever: Busca documentos relevantes en la base de datos vectorial.
   - LLM Provider: Genera respuestas usando modelos de lenguaje (Gemini, Ollama, Groq).
   - DuckDuckGo Fallback: Busca en internet si no hay contexto local suficiente.

4. **Documentos Enriquecidos**: Base de datos procesada por procesar_docs.py con spaCy y BERT NER.

Componentes Principales
-----------------------

app.py - Aplicacion Principal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Framework: Streamlit
* Funciones: UI, cadena RAG, invocacion de LLM
* Patrones: Factory Pattern para LLMs

procesar_docs.py - Pipeline ETL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Extract: PyPDFLoader para cargar PDFs
* Transform: Text splitting + NLP enrichment
* Load: FAISS vectorstore

utils.py - Utilidades
^^^^^^^^^^^^^^^^^^^^^

* Verificacion de configuracion
* Informacion de modelos
* Validacion de preguntas

Flujo de Datos
--------------

1. **Ingesta de Documentos**

   PDFs -> PyPDFLoader -> TextSplitter -> NLP Enrichment -> FAISS

2. **Consulta RAG**

   Pregunta -> Embedding -> FAISS Search -> Contexto -> LLM -> Respuesta

Modelos Utilizados
------------------

* all-MiniLM-L6-v2 (HuggingFace): Embeddings
* es_core_news_lg (spaCy): NER General  
* bert-spanish-ner (HuggingFace): NER Especializado
* mistral:7b (Ollama): Generacion
* gemini-1.5-flash (Google): Generacion
