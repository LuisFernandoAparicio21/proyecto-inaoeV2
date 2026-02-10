# 🤖 Asistente de Investigación INAOE

> **Sistema RAG (Retrieval-Augmented Generation) para consulta inteligente de documentos científicos**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com/)

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Inicio Rápido](#-inicio-rápido)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Componentes](#-componentes)
  - [app.py](#apppy---aplicación-principal)
  - [procesar_docs.py](#procesar_docspy---pipeline-de-procesamiento)
  - [utils.py](#utilspy---funciones-auxiliares)
- [Configuración](#-configuración)
- [Modelos Soportados](#-modelos-soportados)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

---

## 📖 Descripción

El **Asistente de Investigación INAOE** es una aplicación web que permite a los investigadores del Instituto Nacional de Astrofísica, Óptica y Electrónica consultar documentos científicos utilizando inteligencia artificial.

### Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🔍 **Búsqueda Semántica** | Encuentra información relevante usando embeddings vectoriales |
| 🧠 **Multi-LLM** | Soporta Ollama (local), Google Gemini, Groq y Together AI |
| 📚 **Enriquecimiento NLP** | Extrae entidades con spaCy y BERT Spanish NER |
| 🌐 **Fallback Web** | Busca en DuckDuckGo si no hay contexto local suficiente |
| ⚡ **Procesamiento Incremental** | Solo procesa documentos nuevos o modificados |
| 🔒 **Actualización Atómica** | Protege la base de datos de corrupción |

---

## Arquitectura

El sistema se compone de los siguientes elementos:

1. **USUARIO**: Interactua con la interfaz web.
2. **Streamlit UI (app.py)**: Recibe consultas del usuario.
3. **FAISS Retriever**: Busca documentos relevantes en la base vectorial.
4. **LLM Provider**: Genera respuestas (Gemini, Ollama, Groq).
5. **DuckDuckGo Fallback**: Busca en internet si no hay contexto local.
6. **Documentos Enriquecidos**: Procesados por procesar_docs.py con spaCy + BERT NER.

### Flujo de Datos

1. **Usuario** - Ingresa pregunta en Streamlit
2. **FAISS Retriever** - Recupera chunks relevantes (k=5)
3. **Contexto** - Se verifica si es suficiente (mas de 50 chars)
4. **LLM** - Genera respuesta estructurada
5. **Respuesta** - Se muestra con fuentes y tiempo

---

## 🚀 Inicio Rápido

### Requisitos

- Python 3.9+
- 4GB RAM mínimo (8GB recomendado)
- Ollama instalado (opcional, para modelos locales)

### Instalación

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd proyecto_rag_inaoe

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar modelo spaCy
python -m spacy download es_core_news_lg

# 5. Procesar documentos (primera vez)
cd src
python procesar_docs.py

# 6. Ejecutar aplicación
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

---

## 📂 Estructura del Proyecto

```
proyecto_rag_inaoe/
├── src/
│   ├── app.py              # Aplicación Streamlit principal
│   ├── procesar_docs.py    # Pipeline de procesamiento NLP
│   └── utils.py            # Funciones auxiliares
│
├── documentos/             # PDFs y documentos a procesar
│   ├── *.pdf               # Documentos científicos
│   └── *.txt               # Archivos de texto
│
├── models/                 # Modelos descargados
│   ├── bert-spanish-ner/   # BERT NER en español
│   └── sentence-transformers/
│
├── indice_faiss/           # Base de datos vectorial
│   ├── index.faiss         # Índice FAISS
│   └── index.pkl           # Metadatos serializados
│
├── docs/                   # Documentación Mintlify
│
├── .streamlit/
│   └── secrets.toml        # API keys (no en git)
│
├── processed_files.json    # Registro de archivos procesados
├── requirements.txt        # Dependencias Python
└── README.md               # Este archivo
```

---

## 🧩 Componentes

### `app.py` - Aplicación Principal

**Líneas de código:** ~420 | **Propósito:** Interfaz web y cadena RAG

#### Funciones Principales

| Función | Descripción |
|---------|-------------|
| `cargar_base_datos()` | Carga FAISS con embeddings HuggingFace |
| `verificar_ollama()` | Verifica si Ollama está activo en :11434 |
| `get_llm(modelo, temp, timeout)` | Factory para crear instancias LLM |
| `buscar_en_internet(consulta)` | Fallback a DuckDuckGo |
| `render_sidebar()` | Renderiza configuración en sidebar |
| `create_rag_chain()` | Crea la cadena RAG completa |

#### Ejemplo de Uso

```python
from app import get_llm, cargar_base_datos

# Cargar base de datos
db = cargar_base_datos()
retriever = db.as_retriever(search_kwargs={"k": 5})

# Crear LLM
llm = get_llm("gemini-1.5-flash", temperature=0.2, timeout=120)

# Consultar
docs = retriever.get_relevant_documents("¿Qué es un quaternión?")
```

---

### `procesar_docs.py` - Pipeline de Procesamiento

**Líneas de código:** ~400 | **Propósito:** ETL con enriquecimiento NLP

#### Pipeline de Procesamiento

1. PDFs se cargan con PyPDFLoader
2. TextSplitter divide en Chunks
3. Cada chunk se procesa en paralelo por:
   - spaCy NER (modelo es_core_news_lg)
   - BERT Spanish NER (modelo bert-spanish-ner)
4. Los metadatos de ambos modelos se combinan
5. Se almacenan en FAISS con Embeddings

#### Funciones Principales

| Función | Descripción |
|---------|-------------|
| `cargar_registro_archivos()` | Lee JSON con timestamps de archivos |
| `obtener_archivos_a_procesar(registro)` | Detecta archivos nuevos/modificados |
| `procesar_lote_documentos(rutas)` | Carga PDFs y divide en chunks |
| `analizar_chunks_batch(chunks, nlp, hf)` | Enriquece con NLP dual |
| `main()` | Flujo principal con actualización atómica |

#### Configuración del Splitter

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Caracteres por chunk
    chunk_overlap=200,    # Overlap para contexto
    length_function=len
)
```

---

### `utils.py` - Funciones Auxiliares

**Líneas de código:** ~240 | **Propósito:** Utilidades de verificación y validación

#### Funciones

| Función | Descripción |
|---------|-------------|
| `verificar_configuracion()` | Estado del sistema (DB, Ollama, API keys) |
| `obtener_info_modelo(modelo)` | Metadatos de modelos LLM |
| `formatear_tiempo(segundos)` | Convierte segundos a "Xm Ys" |
| `validar_pregunta(pregunta)` | Valida formato de pregunta |

#### Ejemplo

```python
from utils import verificar_configuracion, validar_pregunta

# Verificar sistema
config = verificar_configuracion()
if not config['ollama_disponible']:
    print("Inicia Ollama: ollama serve")

# Validar pregunta
es_valida, msg = validar_pregunta("¿Qué es FAISS?")
print(f"Válida: {es_valida}, Mensaje: {msg}")
```

---

## ⚙️ Configuración

### API Keys

Crea el archivo `.streamlit/secrets.toml`:

```toml
# Google Gemini
GOOGLE_API_KEY = "tu-api-key-de-google"

# Groq (opcional)
GROQ_API_KEY = "tu-api-key-de-groq"

# Together AI (opcional)
TOGETHER_API_KEY = "tu-api-key-de-together"
```

### Obtener API Keys

| Proveedor | URL | Costo |
|-----------|-----|-------|
| Google Gemini | [makersuite.google.com](https://makersuite.google.com) | Gratis (15 req/min) |
| Groq | [console.groq.com](https://console.groq.com) | Pago por uso |
| Together AI | [together.ai](https://together.ai) | $25 créditos gratis |

### Parámetros de la Aplicación

| Parámetro | Rango | Default | Descripción |
|-----------|-------|---------|-------------|
| Documentos | 3-10 | 5 | Chunks a recuperar |
| Creatividad | 0.0-1.0 | 0.2 | Temperature del LLM |
| Timeout | 30-300s | 120s | Tiempo máximo de espera |

---

## 🤖 Modelos Soportados

### Modelos Activos

| Modelo | Proveedor | Tipo | RAM | Notas |
|--------|-----------|------|-----|-------|
| `deepseek-r1:1.5b` | Ollama | Local | ~2GB | Razonamiento avanzado |
| `mistral:7b` | Ollama | Local | 4GB | Excelente para investigación |
| `gemini-1.5-flash` | Google | API | - | Rápido, 15 req/min gratis |
| `gemini-1.5-pro` | Google | API | - | Máxima calidad |

### Modelos NLP

| Modelo | Propósito | Tamaño |
|--------|-----------|--------|
| `es_core_news_lg` | NER general español | ~560MB |
| `bert-spanish-ner` | NER especializado | ~440MB |
| `all-MiniLM-L6-v2` | Embeddings | ~90MB |

---

## 📚 API Reference

### `get_llm(modelo, temperature, timeout)`

Factory que crea instancias de LLM según el proveedor.

**Parámetros:**
- `modelo` (str): ID del modelo (ej: "gemini-1.5-flash")
- `temperature` (float): 0.0-1.0, controla creatividad
- `timeout` (int): Segundos máximos de espera

**Retorna:** Instancia de LLM o None si hay error

**Ejemplo:**
```python
llm = get_llm("mistral:7b", temperature=0.3, timeout=180)
if llm:
    response = llm.invoke("¿Qué es la propulsión de cohetes?")
```

---

### `analizar_chunks_batch(chunks, spacy_nlp, hf_pipeline)`

Analiza un lote de textos con spaCy y HuggingFace.

**Parámetros:**
- `chunks` (List[str]): Lista de textos a analizar
- `spacy_nlp`: Modelo spaCy cargado
- `hf_pipeline`: Pipeline HuggingFace NER

**Retorna:** Lista de diccionarios con entidades extraídas

**Ejemplo:**
```python
metadatos = analizar_chunks_batch(
    ["El INAOE está en Puebla."],
    spacy_nlp,
    hf_pipeline
)
# {'spacy_entities': {'ORG': ['INAOE'], 'LOC': ['Puebla']}, ...}
```

---

### `validar_pregunta(pregunta)`

Valida si una pregunta es apropiada para el sistema.

**Parámetros:**
- `pregunta` (str): Texto de la pregunta

**Retorna:** Tuple[bool, str] - (es_válida, mensaje)

**Reglas:**
- Mínimo 3 caracteres
- Máximo 500 caracteres
- Debe contener palabra interrogativa (qué, cómo, cuál, etc.)

---

## 🚀 Deployment

### Streamlit Cloud

1. Sube a GitHub
2. Conecta en [share.streamlit.io](https://share.streamlit.io)
3. Configura secrets en el dashboard

> ⚠️ Streamlit Cloud no soporta Ollama (solo APIs cloud)

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download es_core_news_lg
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.port=8501"]
```

```bash
docker build -t inaoe-assistant .
docker run -p 8501:8501 inaoe-assistant
```

---

## 🔧 Troubleshooting

### Error: "Base de datos no encontrada"

```bash
cd src
python procesar_docs.py
```

### Error: "Ollama no está ejecutándose"

```bash
# Iniciar servicio Ollama
ollama serve

# Descargar modelo
ollama pull mistral:7b
```

### Error: "spaCy model not found"

```bash
python -m spacy download es_core_news_lg
```

### Error: "CUDA out of memory"

El sistema usa CPU automáticamente si CUDA falla. Para forzar CPU:
```python
device = 'cpu'  # En lugar de 'cuda'
```

---

## 📊 Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Líneas de código Python | ~1,060 |
| Archivos Python | 3 |
| Páginas de documentación | 13 |
| Modelos LLM soportados | 4+ |
| Modelos NLP | 3 |

---

## 📝 Licencia

Este proyecto es para uso interno del INAOE.

---

## 👥 Contribuidores

- Proyecto INAOE

---

*Documentación generada el 26 de Diciembre, 2025*
