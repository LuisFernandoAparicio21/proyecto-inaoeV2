# Documentacion Tecnica Detallada
## Proyecto RAG INAOE - Explicacion Codigo por Codigo

**Version:** 1.0.0  
**Fecha:** 26 de Diciembre, 2025  
**Autor:** Proyecto INAOE

---

## Contenido de esta seccion

- app.py - Aplicacion Principal
- procesar_docs.py - Pipeline de Procesamiento
- utils.py - Funciones Auxiliares
- Flujo de Ejecucion Completo

---

## app.py - Aplicacion Principal

**Propósito:** Interfaz web con Streamlit para consultas RAG sobre documentos científicos.

**Líneas totales:** ~420

---

### Encabezado del Módulo (Líneas 1-26)

```python
"""Asistente de Investigación INAOE - Aplicación RAG con Streamlit.

Esta aplicación proporciona una interfaz web para consultar documentos
científicos del INAOE utilizando Retrieval-Augmented Generation (RAG).
"""
```

**Explicación:**
- El **docstring del módulo** describe el propósito general del archivo
- Sirve como documentación que aparece cuando ejecutas `help(app)`

---

### Imports (Líneas 27-40)

```python
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
import time
import torch
import requests
from typing import List, Dict, Any, Optional, Callable
import os
```

**Explicación de cada import:**

| Import | Propósito |
|--------|-----------|
| `streamlit` | Framework para crear la interfaz web |
| `FAISS` | Base de datos vectorial para búsqueda semántica |
| `HuggingFaceEmbeddings` | Convierte texto a vectores numéricos |
| `PromptTemplate` | Plantilla para formatear prompts al LLM |
| `Path` | Manejo de rutas de archivos multiplataforma |
| `time` | Medir tiempo de respuesta |
| `torch` | Detectar si hay GPU disponible |
| `requests` | Verificar si Ollama está activo |
| `typing` | Anotaciones de tipos para mejor documentación |

---

### Imports de Proveedores LLM (Líneas 42-55)

```python
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama
    from langchain_groq import ChatGroq
    from langchain_together import Together
except ImportError as e:
    st.error(f"Error al importar: {e}")
    st.stop()
```

**Explicación:**
- **try/except:** Captura errores si falta alguna dependencia
- Si falla, muestra error en Streamlit y detiene la ejecución
- Esto evita que la app crashee sin dar información al usuario

---

### Configuración de Página Streamlit (Líneas 57-63)

```python
st.set_page_config(
    page_title="Asistente INAOE 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Explicación:**
- `page_title`: Título que aparece en la pestaña del navegador
- `page_icon`: Emoji/icono de la pestaña
- `layout="wide"`: Usa todo el ancho de la pantalla
- `initial_sidebar_state`: El sidebar se muestra expandido al inicio

---

### Configuración de Rutas (Líneas 65-67)

```python
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DB = RUTA_PROYECTO / "indice_faiss"
```

**Explicación:**
- `Path(__file__)`: Ruta del archivo actual (app.py)
- `.resolve()`: Convierte a ruta absoluta
- `.parent.parent`: Sube dos niveles (src → proyecto_rag_inaoe)
- `/`: Operador de Path para unir rutas de forma segura

**Ejemplo:**
```
__file__ = C:/proyecto/src/app.py
.parent = C:/proyecto/src
.parent.parent = C:/proyecto
/ "indice_faiss" = C:/proyecto/indice_faiss
```

---

### Configuración de Modelos (Líneas 70-102)

```python
MODEL_CONFIG = {
    "deepseek-r1:1.5b": {
        "provider": "ollama", 
        "info": "🚀 Local DeepSeek - Razonamiento avanzado, ~2GB RAM."
    },
    "mistral:7b": {
        "provider": "ollama", 
        "info": "🏆 Local - Excelente para investigación, 4GB RAM."
    },
    "gemini-1.5-flash": {
        "provider": "google", 
        "info": "🟢 API Google - Rápido, 15 req/min gratis."
    },
    "gemini-1.5-pro": {
        "provider": "google", 
        "info": "✨ API Google - Máxima calidad de razonamiento."
    },
}
```

**Explicación:**
- **Diccionario** que mapea IDs de modelos a sus configuraciones
- `provider`: Indica qué API/servicio usar (ollama, google, groq, together)
- `info`: Texto descriptivo que se muestra al usuario en el sidebar
- Para agregar un nuevo modelo, solo se añade una entrada aquí

---

### Template del Prompt (Líneas 104-143)

```python
PROMPT_TEMPLATE = """
Eres un Asistente de Investigación Senior del INAOE...

**MISIÓN PRINCIPAL:**
1. PRIORIDAD 1: El CONTEXTO de documentos INAOE
2. PRIORIDAD 2: Conocimiento general del modelo
3. PRIORIDAD 3: Fuentes verificables
4. PRIORIDAD 4: Búsqueda en internet

**FORMATO DE SALIDA:**
- Resumen Ejecutivo (TL;DR)
- Análisis Detallado
- Conclusión e Implicaciones
- Fuentes Consultadas

---
**CONTEXTO PROPORCIONADO:**
{context}

**PREGUNTA DEL INVESTIGADOR:**
{question}
"""
```

**Explicación:**
- **Prompt Engineering:** Define cómo el LLM debe responder
- `{context}`: Placeholder que se reemplaza con documentos recuperados
- `{question}`: Placeholder para la pregunta del usuario
- El formato estructurado garantiza respuestas consistentes

---

### Función: buscar_en_internet() (Líneas 145-195)

```python
def buscar_en_internet(consulta: str, max_resultados: int = 5) -> List[str]:
    """Realiza una búsqueda web usando DuckDuckGo como fallback."""
    try:
        from duckduckgo_search import DDGS
    except Exception as e:
        return [f"[Fallback deshabilitado] {e}"]

    try:
        resultados = []
        with DDGS() as ddgs:
            for item in ddgs.text(consulta, region="wt-wt", 
                                   safesearch="moderate", 
                                   max_results=max_resultados):
                titulo = item.get("title", "")
                cuerpo = item.get("body", "")
                link = item.get("href", "")
                resultados.append(f"Título: {titulo}\nResumen: {cuerpo}\nFuente: {link}")
        return resultados if resultados else ["No se encontraron resultados."]
    except Exception as e:
        return [f"Error en búsqueda web: {e}"]
```

**Explicación línea por línea:**

| Línea | Código | Explicación |
|-------|--------|-------------|
| 1 | `def buscar_en_internet(...)` | Define función con tipos de parámetros |
| 2-4 | `try: from duckduckgo...` | Importa la librería bajo demanda |
| 5 | `resultados = []` | Lista vacía para almacenar resultados |
| 6 | `with DDGS() as ddgs:` | Context manager para manejar conexión |
| 7 | `for item in ddgs.text(...)` | Itera sobre resultados de búsqueda |
| 8-10 | `item.get(...)` | Extrae campos de forma segura (evita KeyError) |
| 11 | `resultados.append(...)` | Formatea y agrega cada resultado |
| 12 | `return resultados if...` | Retorna resultados o mensaje de error |

---

### Función: cargar_base_datos() (Líneas 197-240)

```python
@st.cache_resource
def cargar_base_datos() -> Optional[FAISS]:
    """Carga la base de datos vectorial FAISS de forma segura."""
    if not RUTA_DB.exists():
        st.error(f"❌ No se encontró la base de datos en: {RUTA_DB}")
        st.info("💡 Ejecuta primero: `python procesar_docs.py`")
        return None
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': device},
            cache_folder=str(RUTA_PROYECTO / "models"),
            encode_kwargs={'normalize_embeddings': True}
        )
        return FAISS.load_local(str(RUTA_DB), embeddings, 
                                 allow_dangerous_deserialization=True)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return None
```

**Explicación:**

| Elemento | Explicación |
|----------|-------------|
| `@st.cache_resource` | **Decorador** que cachea el resultado. La función solo se ejecuta una vez por sesión |
| `Optional[FAISS]` | Puede retornar una instancia de FAISS o None |
| `RUTA_DB.exists()` | Verifica si el directorio existe |
| `torch.cuda.is_available()` | Detecta si hay GPU NVIDIA disponible |
| `HuggingFaceEmbeddings(...)` | Crea el modelo de embeddings |
| `model_kwargs={'device': device}` | Indica si usar GPU o CPU |
| `cache_folder=...` | Guarda modelos localmente para no re-descargar |
| `normalize_embeddings=True` | Normaliza vectores para mejor similitud coseno |
| `FAISS.load_local(...)` | Carga el índice desde disco |
| `allow_dangerous_deserialization=True` | Necesario para cargar objetos pickle |

---

### Función: verificar_ollama() (Líneas 242-268)

```python
@st.cache_data(ttl=300)
def verificar_ollama() -> bool:
    """Verifica si el servicio de Ollama está activo en localhost."""
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True
    except requests.ConnectionError:
        return False
```

**Explicación:**

| Elemento | Explicación |
|----------|-------------|
| `@st.cache_data(ttl=300)` | Cachea el resultado por 5 minutos (300 segundos) |
| `ttl` | Time To Live - después de 300s, vuelve a verificar |
| `requests.get(...)` | Hace petición HTTP GET al puerto de Ollama |
| `timeout=3` | Espera máximo 3 segundos |
| `ConnectionError` | Se lanza si Ollama no está corriendo |

---

### Función: get_llm() - Factory Pattern (Líneas 292-356)

```python
def get_llm(modelo: str, temperature: float, timeout: int) -> Optional[Any]:
    """Factory que crea instancias de LLM según el proveedor."""
    config = MODEL_CONFIG.get(modelo, {})
    provider = config.get("provider")

    if provider == "google":
        if 'GOOGLE_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Google")
            return None
        return ChatGoogleGenerativeAI(
            model=modelo.split('/')[-1], 
            api_key=st.secrets["GOOGLE_API_KEY"], 
            temperature=temperature
        )
    
    elif provider == "ollama":
        if not verificar_ollama():
            st.error("🚨 Ollama no está ejecutándose")
            return None
        return ChatOllama(
            model=modelo, 
            temperature=temperature, 
            timeout=timeout
        )
        
    elif provider == "groq":
        # Similar a Google...
        
    elif provider == "together":
        # Similar a Google...
        
    else:
        st.error(f"🚨 Proveedor '{provider}' no configurado")
        return None
```

**Explicación del Patrón Factory:**

```
+-------------------+
|  get_llm()        | <-- Entrada: modelo, temperature, timeout
+-------------------+
| if google:        | --> ChatGoogleGenerativeAI
| elif ollama:      | --> ChatOllama
| elif groq:        | --> ChatGroq
| elif together:    | --> Together
| else:             | --> None + Error
+-------------------+
```

**Ventajas del Factory Pattern:**
1. **Centralizado:** Solo un lugar para crear LLMs
2. **Extensible:** Agregar nuevo proveedor = agregar elif
3. **Encapsulado:** La lógica de creación está oculta del resto del código

---

### Función: render_sidebar() (Líneas 358-394)

```python
def render_sidebar() -> tuple[str, int, float, int]:
    """Renderiza la barra lateral con opciones de configuración."""
    st.sidebar.header("⚙️ Configuración")
    
    modelo_seleccionado = st.sidebar.selectbox(
        "Selecciona el modelo:",
        list(MODEL_CONFIG.keys()),
        index=0
    )
    
    st.sidebar.info(MODEL_CONFIG[modelo_seleccionado]["info"])

    with st.sidebar.expander("🔧 Configuración Avanzada"):
        chunk_size = st.slider("Documentos a consultar", 3, 10, 5)
        temperature = st.slider("Creatividad", 0.0, 1.0, 0.2)
        timeout = st.slider("Timeout (segundos)", 30, 300, 120)
        
    return modelo_seleccionado, chunk_size, temperature, timeout
```

**Explicación de Widgets:**

| Widget | Código | Descripción |
|--------|--------|-------------|
| `selectbox` | Dropdown para seleccionar modelo | Muestra lista de modelos |
| `info` | Cuadro informativo | Muestra descripción del modelo |
| `expander` | Sección colapsable | Oculta configuración avanzada |
| `slider` | Deslizador | Permite seleccionar valores numéricos |

**Valores de retorno:**
- `modelo_seleccionado`: String con ID del modelo
- `chunk_size`: Entero (3-10)
- `temperature`: Float (0.0-1.0)
- `timeout`: Entero (30-300)

---

### Función: main() - Flujo Principal (Líneas 396-480)

```python
def main():
    st.title("Asistente de Investigación INAOE 🤖")
    st.write("Hazme preguntas sobre los documentos del INAOE...")

    # 1. Configuración del sidebar
    modelo_sel, chunk_size, temp, timeout = render_sidebar()

    # 2. Cargar base de datos
    db = cargar_base_datos()
    if db is None:
        return
        
    # 3. Crear LLM
    llm = get_llm(modelo_sel, temp, timeout)
    if llm is None:
        return

    # 4. Crear retriever
    retriever = db.as_retriever(search_kwargs={"k": chunk_size})
    
    # 5. Crear prompt
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    
    # 6. Crear cadena RAG
    def create_rag_chain():
        def rag_invoke(question):
            docs = retriever.get_relevant_documents(question)
            context = format_docs(docs)
            
            # Fallback a internet si contexto insuficiente
            if not context or len(context.strip()) < 50:
                resultados_web = buscar_en_internet(question)
                context = f"[Fuente: Internet]\n{'\n'.join(resultados_web)}"
            
            formatted_prompt = prompt.format(context=context, question=question)
            response = llm.invoke(formatted_prompt)
            
            return {
                "context": context,
                "question": question,
                "answer": response.content
            }
        return rag_invoke
    
    rag_chain = create_rag_chain()

    # 7. Interfaz de entrada
    pregunta = st.text_input("🤔 ¿Qué te gustaría saber?")
    
    if st.button("🔍 Buscar respuesta") and pregunta:
        with st.spinner(f"🤖 Buscando respuesta con {modelo_sel}..."):
            start_time = time.time()
            result = rag_chain(pregunta)
            end_time = time.time()

            st.markdown("### 📝 Respuesta:")
            st.write(result["answer"])
            st.metric("⏱️ Tiempo", f"{end_time - start_time:.2f}s")

if __name__ == "__main__":
    main()
```

**Diagrama de Flujo:**

```
main()
  |
  +-- render_sidebar() --> Configuracion
  |
  +-- cargar_base_datos() --> FAISS DB
  |         |
  |         +-- Si falla --> return
  |
  +-- get_llm() --> Instancia LLM
  |         |
  |         +-- Si falla --> return
  |
  +-- as_retriever() --> Retriever configurado
  |
  +-- create_rag_chain() --> Funcion RAG
  |
  +-- st.button() --> Si click:
            |
            +-- rag_chain(pregunta)
            |       |
            |       +-- Recuperar documentos
            |       +-- Verificar contexto
            |       +-- Fallback a web si necesario
            |       +-- Formatear prompt
            |       +-- Invocar LLM
            |
            +-- Mostrar respuesta + tiempo
```

---

## procesar_docs.py - Pipeline de Procesamiento

**Propósito:** Pipeline ETL para procesar PDFs con enriquecimiento NLP

**Líneas totales:** ~400

---

### Módulo Docstring (Líneas 1-32)

```python
"""Pipeline de procesamiento de documentos para el sistema RAG INAOE.

Este módulo implementa un pipeline ETL (Extract, Transform, Load) para:
- Extract: Cargar documentos PDF
- Transform: Dividir en chunks y enriquecer con NLP
- Load: Almacenar en base de datos vectorial FAISS
"""
```

---

### Configuración Centralizada (Líneas 50-66)

```python
# Rutas
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
DIR_DOCS = RUTA_PROYECTO / "documentos"
DIR_DB_FAISS = RUTA_PROYECTO / "indice_faiss"
DIR_DB_TEMP = RUTA_PROYECTO / "indice_faiss_temp"  # Para atomicidad
ARCHIVO_REGISTRO = RUTA_PROYECTO / "processed_files.json"

# Modelos
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL = "es_core_news_lg"
RUTA_MODELO_HF = RUTA_PROYECTO / "models" / "bert-spanish-ner"
```

**Explicación:**

| Variable | Propósito |
|----------|-----------|
| `DIR_DOCS` | Carpeta con PDFs de entrada |
| `DIR_DB_FAISS` | Carpeta con índice FAISS final |
| `DIR_DB_TEMP` | Carpeta temporal para actualización atómica |
| `ARCHIVO_REGISTRO` | JSON que trackea archivos procesados |
| `EMBEDDING_MODEL` | Modelo para convertir texto a vectores |
| `SPACY_MODEL` | Modelo de spaCy para NER español |
| `RUTA_MODELO_HF` | Carpeta local con modelo BERT |

---

### Sistema de Registro Incremental (Líneas 68-118)

```python
def cargar_registro_archivos() -> Dict[str, float]:
    """Carga el registro de archivos procesados desde JSON."""
    if not ARCHIVO_REGISTRO.exists():
        return {}
    with open(ARCHIVO_REGISTRO, 'r') as f:
        return json.load(f)

def guardar_registro_archivos(registro: Dict[str, float]) -> None:
    """Guarda el registro actualizado."""
    with open(ARCHIVO_REGISTRO, 'w') as f:
        json.dump(registro, f, indent=4)

def obtener_archivos_a_procesar(registro: Dict[str, float]) -> List[str]:
    """Determina qué archivos son nuevos o modificados."""
    archivos_nuevos = []
    for archivo_pdf in DIR_DOCS.glob("*.pdf"):
        nombre_archivo = str(archivo_pdf)
        ultima_modificacion = os.path.getmtime(nombre_archivo)
        
        # Comparar timestamp
        if nombre_archivo not in registro or registro[nombre_archivo] < ultima_modificacion:
            archivos_nuevos.append(nombre_archivo)
            registro[nombre_archivo] = ultima_modificacion
            
    return archivos_nuevos
```

**Estructura del JSON de registro:**

```json
{
    "C:/proyecto/docs/paper1.pdf": 1702857600.0,
    "C:/proyecto/docs/paper2.pdf": 1702944000.0
}
```

**Lógica de detección:**

```
archivo en disco    registro JSON         acción
─────────────────   ───────────────       ──────
timestamp: 1000     no existe             PROCESAR (nuevo)
timestamp: 2000     timestamp: 1000       PROCESAR (modificado)
timestamp: 1000     timestamp: 1000       IGNORAR (sin cambios)
```

---

### Procesamiento de Documentos (Líneas 163-209)

```python
def procesar_lote_documentos(rutas_archivos: List[str]) -> List[Any]:
    """Carga y divide en chunks un lote de documentos PDF."""
    documentos = []
    
    # Cargar cada PDF
    for ruta in rutas_archivos:
        try:
            loader = PyPDFLoader(ruta)
            documentos.extend(loader.load())
            logging.info(f"Cargado: {Path(ruta).name}")
        except Exception as e:
            logging.error(f"Error cargando {ruta}: {e}")
            continue  # Continúa con el siguiente
    
    if not documentos:
        return []

    # Dividir en chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Caracteres por chunk
        chunk_overlap=200,    # Overlap entre chunks
        length_function=len
    )
    return splitter.split_documents(documentos)
```

**Visualización del Splitting:**

```
Documento Original:
┌────────────────────────────────────────────────────────────┐
│ Lorem ipsum dolor sit amet, consectetur adipiscing elit.   │
│ Sed do eiusmod tempor incididunt ut labore et dolore...    │
│ [... 5000 caracteres ...]                                  │
└────────────────────────────────────────────────────────────┘

Después de split (chunk_size=1000, overlap=200):

Chunk 1:                    Chunk 2:                    Chunk 3:
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│ Lorem ipsum...   │       │ ...tempor inci...│       │ ...et dolore...  │
│ (1000 chars)     │       │ (1000 chars)     │       │ (1000 chars)     │
└──────────────────┘       └──────────────────┘       └──────────────────┘
         │                          │                          │
         └──────── 200 chars ───────┘──────── 200 chars ───────┘
                   (overlap)                   (overlap)
```

**¿Por qué overlap?**
- Mantiene contexto entre chunks
- Evita cortar ideas a la mitad
- Mejora la recuperación de información

---

### Enriquecimiento NLP - analizar_chunks_batch() (Líneas 213-291)

```python
@torch.no_grad()
def analizar_chunks_batch(
    chunks_texto: List[str],
    spacy_nlp: Any,
    hf_pipeline: Any
) -> List[Dict[str, Dict[str, List[str]]]]:
    """Analiza un lote de textos con spaCy y HuggingFace."""
    metadatos_enriquecidos = []

    # Estación 1: spaCy - Procesamiento batch
    spacy_docs = list(spacy_nlp.pipe(chunks_texto))
    
    # Estación 2: HuggingFace - Procesamiento batch
    try:
        hf_results = hf_pipeline(chunks_texto)
    except Exception as e:
        logging.error(f"Error en HuggingFace: {e}")
        hf_results = [[] for _ in chunks_texto]

    # Combinar resultados
    for i, doc in enumerate(spacy_docs):
        # Extraer entidades de spaCy
        entidades_spacy: Dict[str, List[str]] = {}
        for ent in doc.ents:
            if ent.label_ not in entidades_spacy:
                entidades_spacy[ent.label_] = []
            entidades_spacy[ent.label_].append(ent.text)
        
        # Extraer entidades de HuggingFace
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
```

**Diagrama del Pipeline NLP:**

```
                    Chunks de Texto
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
   ┌─────────────┐                 ┌─────────────┐
   │   spaCy     │                 │    BERT     │
   │ es_core_    │                 │  spanish    │
   │ news_lg     │                 │    ner      │
   └─────┬───────┘                 └─────┬───────┘
         │                               │
         ▼                               ▼
   ┌─────────────┐                 ┌─────────────┐
   │ Entidades:  │                 │ Entidades:  │
   │ ORG: INAOE  │                 │ ORG: Inst.  │
   │ LOC: Puebla │                 │ PER: Juan   │
   │ PER: María  │                 │ LOC: México │
   └─────────────┘                 └─────────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
               ┌─────────────────┐
               │ Metadatos       │
               │ Combinados      │
               │ {spacy: {...},  │
               │  hf: {...}}     │
               └─────────────────┘
```

**Tipos de entidades detectadas:**

| Etiqueta | Significado | Ejemplo |
|----------|-------------|---------|
| ORG | Organización | INAOE, NASA |
| PER | Persona | Juan García |
| LOC | Lugar | Puebla, México |
| MISC | Misceláneos | Quaterniones |
| DATE | Fecha | 2024 |

---

### Actualización Atómica de FAISS (Líneas 340-380)

```python
# Paso 1: Eliminar directorio temporal si existe
if DIR_DB_TEMP.exists():
    shutil.rmtree(DIR_DB_TEMP)

# Paso 2: Cargar o crear base de datos
if DIR_DB_FAISS.exists() and chunks_nuevos:
    logging.info("Cargando base existente para fusionar...")
    db_existente = FAISS.load_local(str(DIR_DB_FAISS), embeddings, 
                                     allow_dangerous_deserialization=True)
    db_existente.add_documents(chunks_nuevos)
    db_final = db_existente
elif chunks_nuevos:
    logging.info("Creando nueva base de datos...")
    db_final = FAISS.from_documents(chunks_nuevos, embeddings)
else:
    return

# Paso 3: Guardar en directorio temporal
db_final.save_local(str(DIR_DB_TEMP))

# Paso 4: Reemplazo atómico
if DIR_DB_FAISS.exists():
    shutil.rmtree(DIR_DB_FAISS)
os.rename(DIR_DB_TEMP, DIR_DB_FAISS)

# Paso 5: Actualizar registro
guardar_registro_archivos(registro_archivos)
```

**¿Por qué Actualización Atómica?**

```
Sin Atomicidad (PELIGROSO):
─────────────────────────
1. Borrar índice antiguo     ←── Si falla aquí, PERDEMOS TODO
2. Guardar índice nuevo      ←── Si falla aquí, NO HAY ÍNDICE

Con Atomicidad (SEGURO):
────────────────────────
1. Guardar en indice_temp    ←── Si falla, índice original intacto
2. Borrar índice antiguo
3. Renombrar temp → final    ←── Operación atómica del OS
```

---

## utils.py - Funciones Auxiliares

**Propósito:** Utilidades de verificación, información de modelos y validación

**Líneas totales:** ~270

---

### verificar_configuracion() (Líneas 37-95)

```python
def verificar_configuracion() -> Dict[str, Any]:
    """Verifica la configuración del proyecto y retorna el estado."""
    config = {
        "base_datos_existe": False,
        "ollama_disponible": False,
        "api_keys_configuradas": False,
        "errores": []
    }
    
    # Check 1: Base de datos FAISS
    ruta_db = ruta_proyecto / "indice_faiss"
    if ruta_db.exists() and (ruta_db / "index.faiss").exists():
        config["base_datos_existe"] = True
    else:
        config["errores"].append("Base de datos no encontrada")
    
    # Check 2: Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            config["ollama_disponible"] = True
    except:
        config["errores"].append("Ollama no ejecutándose")
    
    # Check 3: API Keys
    try:
        if 'GOOGLE_API_KEY' in st.secrets:
            config["api_keys_configuradas"] = True
    except:
        config["errores"].append("No se pudo verificar API keys")
    
    return config
```

**Uso típico:**

```python
config = verificar_configuracion()
if config["errores"]:
    print("Problemas encontrados:")
    for error in config["errores"]:
        print(f"  - {error}")
else:
    print("✅ Sistema configurado correctamente")
```

---

### validar_pregunta() (Líneas 230-270)

```python
def validar_pregunta(pregunta: str) -> Tuple[bool, str]:
    """Valida si una pregunta es apropiada para el sistema."""
    # Validación 1: Longitud mínima
    if not pregunta or len(pregunta.strip()) < 3:
        return False, "Mínimo 3 caracteres"
    
    # Validación 2: Longitud máxima
    if len(pregunta) > 500:
        return False, "Máximo 500 caracteres"
    
    # Validación 3: Palabras interrogativas
    palabras_clave = [
        "qué", "cuál", "cómo", "dónde", "cuándo", "por qué", "quién",
        "what", "how", "where", "when", "why", "who"
    ]
    
    pregunta_lower = pregunta.lower()
    tiene_palabra_clave = any(p in pregunta_lower for p in palabras_clave)
    
    if not tiene_palabra_clave:
        return False, "Debe contener palabra interrogativa"
    
    return True, "Pregunta válida"
```

**Tabla de validaciones:**

| Entrada | Resultado | Mensaje |
|---------|-----------|---------|
| `""` | False | Mínimo 3 caracteres |
| `"Hola"` | False | Debe contener palabra interrogativa |
| `"¿Qué es FAISS?"` | True | Pregunta válida |
| `"A" * 600` | False | Máximo 500 caracteres |

---

## Flujo de Ejecucion Completo

### Primer Uso (Procesamiento Inicial)

```
Terminal:
$ python procesar_docs.py

Flujo:
────────────────────────────────────────────────────────────
1. Cargar modelos NLP
   ├── spacy.load("es_core_news_lg")        # ~560MB
   └── pipeline("ner", model="bert-spanish") # ~440MB

2. Cargar registro de archivos
   └── processed_files.json (vacío o existente)

3. Detectar archivos a procesar
   ├── Escanear documentos/*.pdf
   └── Comparar timestamps con registro

4. Procesar documentos
   ├── PyPDFLoader para cada PDF
   └── RecursiveCharacterTextSplitter → chunks

5. Enriquecer con NLP
   ├── spaCy: Extraer entidades generales
   └── BERT: Extraer entidades especializadas

6. Crear/actualizar FAISS
   ├── HuggingFaceEmbeddings para vectorizar
   ├── Guardar en directorio temporal
   └── Reemplazo atómico

7. Actualizar registro
   └── Guardar timestamps en JSON
────────────────────────────────────────────────────────────
Resultado: indice_faiss/ con index.faiss + index.pkl
```

---

### Uso Normal (Consulta)

```
Navegador: http://localhost:8501

Flujo de una consulta:
────────────────────────────────────────────────────────────
Usuario: "¿Qué es un quaternión?"
           │
           ▼
1. render_sidebar()
   └── Modelo: mistral:7b, Chunks: 5, Temp: 0.2

2. cargar_base_datos()  (cacheado)
   └── FAISS con embeddings

3. get_llm("mistral:7b", 0.2, 120)
   └── ChatOllama configurado

4. retriever.get_relevant_documents("¿Qué es un quaternión?")
   ├── Embedding de la pregunta
   ├── Búsqueda de similitud en FAISS
   └── Top 5 chunks relevantes

5. Verificar contexto
   ├── Si len(contexto) >= 50: usar contexto local
   └── Si len(contexto) < 50: buscar_en_internet()

6. prompt.format(context=..., question=...)
   └── Prompt formateado con plantilla

7. llm.invoke(formatted_prompt)
   └── Respuesta del modelo

8. Mostrar en UI
   ├── st.write(respuesta)
   ├── st.metric("Tiempo", "2.5s")
   └── st.expander("Fuentes") con contexto
────────────────────────────────────────────────────────────
```

---

### Flujo de Interaccion Entre Componentes

El sistema sigue la siguiente secuencia de interacciones:

1. **Usuario envia pregunta** a la interfaz Streamlit

2. **Streamlit solicita documentos** a FAISS
   - FAISS retorna los 5 chunks mas relevantes

3. **Verificacion de contexto**:
   - Si el contexto tiene menos de 50 caracteres, se activa fallback
   - Streamlit solicita resultados a DuckDuckGo (Web)
   - Web retorna resultados de busqueda

4. **Generacion de respuesta**:
   - Streamlit envia el prompt con contexto al LLM
   - LLM procesa y genera la respuesta

5. **Respuesta al usuario**:
   - Streamlit muestra la respuesta formateada al usuario

---

*Fin de la Documentacion Tecnica*

