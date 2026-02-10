"""Asistente de Investigación INAOE - Aplicación RAG con Streamlit.

Esta aplicación proporciona una interfaz web para consultar documentos
científicos del INAOE utilizando Retrieval-Augmented Generation (RAG).
Soporta múltiples proveedores de LLM incluyendo Ollama (local) y APIs
cloud como Google Gemini, Groq y Together AI.

Modules:
    streamlit: Framework web para la interfaz de usuario.
    langchain: Orquestación de cadenas RAG y LLMs.
    faiss: Base de datos vectorial para búsqueda semántica.
    torch: Soporte GPU para embeddings.

Example:
    Para ejecutar la aplicación:
    
    $ cd src
    $ streamlit run app.py

Author:
    Proyecto INAOE
    
Version:
    1.0.0
"""

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

# Configurar variables de entorno para modo offline (comentado temporalmente)
# os.environ["HF_HUB_OFFLINE"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"

# --- Importaciones de Modelos Específicos ---

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama
    # Las siguientes se pueden añadir a requirements.txt cuando se activen sus modelos
    from langchain_groq import ChatGroq
    from langchain_together import Together
except ImportError as e:
    st.error(f"Error al importar una librería de LangChain: {e}. Por favor, ejecuta 'pip install -r requirements.txt'")
    st.stop()

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Asistente INAOE 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constantes y Configuración de Modelos ---
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DB = RUTA_PROYECTO / "indice_faiss"


MODEL_CONFIG = {
    # --- Modelos Activos ---
    "deepseek-r1:1.5b": {
        "provider": "ollama", 
        "info": "🚀 Local DeepSeek - Razonamiento avanzado, ligero (1.5B params), gratis, ~2GB RAM."
    },
    "mistral:7b": {
        "provider": "ollama", 
        "info": "🏆 Local - Excelente para investigación, gratis, requiere 4GB RAM."
    },
    "gemini-1.5-flash": {
        "provider": "google", 
        "info": "🟢 API Google - Rápido y preciso, requiere API key, 15 req/min gratis."
    },
    "gemini-1.5-pro": {
        "provider": "google", 
        "info": "✨ API Google - Máxima calidad de razonamiento, más lento y costoso."
    },

    # --- Modelos  ---
    # "llama3.2:3b": {
    #     "provider": "ollama", 
    #     "info": "🟢 Local - Buen balance calidad/velocidad, gratis, 2GB RAM."
    # },
    # "llama3-8b-8192": {
    #     "provider": "groq", 
    #     "info": "🟡 API Groq - Muy rápido, requiere API key."
    # },
    # "together/llama-2-7b-chat": {
    #     "provider": "together", 
    #     "info": "🟢 API Together - $25 créditos gratis, alta calidad."
    # },
}

PROMPT_TEMPLATE = """
Eres un Asistente de Investigación Senior del INAOE. Tu propósito es actuar como un colega experto para apoyar a los investigadores. Responde siempre en español, con un lenguaje técnico preciso y una estructura clara.

**MISIÓN PRINCIPAL:**
Tu misión es sintetizar información de tres fuentes en orden de prioridad para construir una respuesta completa y profunda:
1.  **PRIORIDAD 1 (VERDAD FUNDAMENTAL):** El `CONTEXTO` extraído de los documentos internos del INAOE. Esta es tu principal fuente de verdad.
2.  **PRIORIDAD 2 (CONOCIMIENTO GENERAL):** Tu vasto conocimiento interno sobre ciencia, tecnología y el estado del arte en las áreas de investigación relevantes.
3.  **PRIORIDAD 3 (FUENTES VERIFICABLES):** Principios y datos de fuentes académicas y científicas universalmente aceptadas.
4.  **PRIORIDAD 4 (PROMPTS SIN INFORMAICON EN LA BASE DE DATOS):** Si no hay información en la base de datos, se debe buscar en internet o  en tu modelo local.

**REGLAS DE OPERACIÓN ESTRICTAS:**
1.  **FUSIONA Y CONTRASTA:** No te limites a repetir el `CONTEXTO`. Analízalo, compáralo con el conocimiento científico establecido (Prioridad 2 y 3), y extrae conclusiones e implicaciones. Si el `CONTEXTO` presenta una idea novedosa o una discrepancia, señálalo.
2.  **EXPANDE CON CONOCIMIENTO EXTERNO:** Si el `CONTEXTO` es insuficiente para una respuesta completa, enriquécela proactivamente con tu conocimiento interno, pero siempre diferenciando: "Según los documentos proporcionados..." y "Adicionalmente, en el campo más amplio de la astrofísica, se sabe que...".
3.  **CERO ALUCINACIONES:** La rigurosidad es absoluta. Nunca inventes información. Si un tema es teórico, especulativo o está en los límites del conocimiento, indícalo claramente. No presentes una hipótesis como un hecho establecido.
4.  **CITA TUS FUENTES RIGUROSAMENTE:** Al final de tu respuesta, DEBES incluir una sección de "Fuentes Consultadas" que liste los metadatos (`source` y `page`) de los documentos del `CONTEXTO` que utilizaste para formular tu respuesta.

**FORMATO DE SALIDA OBLIGATORIO:**
Debes estructurar tu respuesta de la siguiente manera:

**Resumen Ejecutivo (TL;DR):**
(Una o dos frases que resumen la respuesta a la pregunta directamente. Ideal para un investigador ocupado.)

**Análisis Detallado:**
(Aquí desarrollas la respuesta en profundidad. Usa listas con viñetas o numeradas para estructurar la información, desglosando los puntos clave, las metodologías, los datos y las comparaciones.)

**Conclusión e Implicaciones:**
(Aquí sintetizas las conclusiones. ¿Qué significa esta información? ¿Cuáles son los siguientes pasos lógicos en la investigación? ¿Qué implicaciones tiene para el INAOE o para el campo de estudio?)

**Fuentes Consultadas (Documentos INAOE):**
- Documento: [nombre del archivo fuente del chunk 1], Página: [número de página]
- Documento: [nombre del archivo fuente del chunk 2], Página: [número de página]
- ... (y así sucesivamente para cada documento relevante del contexto)

---
**CONTEXTO PROPORCIONADO:**
{context}

**PREGUNTA DEL INVESTIGADOR:**
{question}
"""

# --- Búsqueda en Internet (fallback) ---
def buscar_en_internet(consulta: str, max_resultados: int = 5) -> List[str]:
    """Realiza una búsqueda web usando DuckDuckGo como fallback.
    
    Esta función se utiliza cuando el contexto local de la base de datos
    FAISS es insuficiente para responder la consulta del usuario.
    
    Args:
        consulta (str): El texto de búsqueda a enviar a DuckDuckGo.
        max_resultados (int, optional): Número máximo de resultados a retornar.
            Por defecto es 5.
    
    Returns:
        List[str]: Lista de strings formateados con título, resumen y URL
            de cada resultado. Retorna un mensaje de error si la búsqueda falla.
    
    Raises:
        No lanza excepciones directamente, los errores se capturan y retornan
        como strings en la lista de resultados.
    
    Example:
        >>> resultados = buscar_en_internet("quaterniones rotación")
        >>> print(resultados[0])
        Título: Quaterniones en Rotación 3D
        Resumen: Los quaterniones son una extensión...
        Fuente: https://ejemplo.com/quaterniones
    """
    try:
        from duckduckgo_search import DDGS
    except Exception as e:
        return [f"[Fallback deshabilitado] No se pudo importar duckduckgo-search: {e}"]

    try:
        resultados = []
        with DDGS() as ddgs:
            for item in ddgs.text(consulta, region="wt-wt", safesearch="moderate", max_results=max_resultados):
                titulo = item.get("title", "")
                cuerpo = item.get("body", "")
                link = item.get("href", "")
                resultados.append(f"Título: {titulo}\nResumen: {cuerpo}\nFuente: {link}")
        return resultados if resultados else ["No se encontraron resultados web relevantes."]
    except Exception as e:
        return [f"Error en búsqueda web: {e}"]

# --- Funciones de Carga y Configuración (Cacheadas) ---

@st.cache_resource
def cargar_base_datos() -> Optional[FAISS]:
    """Carga la base de datos vectorial FAISS de forma segura.
    
    Inicializa los embeddings de HuggingFace y carga el índice FAISS
    desde el directorio local. Utiliza GPU si está disponible.
    
    El decorador @st.cache_resource asegura que la base de datos
    solo se cargue una vez por sesión de Streamlit.
    
    Args:
        None
    
    Returns:
        Optional[FAISS]: Instancia de la base de datos vectorial FAISS
            cargada y lista para consultas, o None si ocurre un error.
    
    Raises:
        Muestra errores en la UI de Streamlit en lugar de lanzar excepciones.
    
    Note:
        - Usa 'cuda' si hay GPU NVIDIA disponible, 'cpu' en caso contrario.
        - Los modelos se cachean en la carpeta 'models/' del proyecto.
        - Requiere ejecutar primero `python procesar_docs.py`.
    """
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
        return FAISS.load_local(str(RUTA_DB), embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return None

@st.cache_data(ttl=300)
def verificar_ollama() -> bool:
    """Verifica si el servicio de Ollama está activo en localhost.
    
    Realiza una petición HTTP GET al endpoint de Ollama para verificar
    que el servicio está ejecutándose y puede recibir solicitudes.
    
    El decorador @st.cache_data con ttl=300 cachea el resultado por
    5 minutos para evitar verificaciones constantes.
    
    Args:
        None
    
    Returns:
        bool: True si Ollama responde correctamente, False si hay
            error de conexión o timeout.
    
    Example:
        >>> if verificar_ollama():
        ...     print("Ollama está listo")
        ... else:
        ...     print("Inicia Ollama con: ollama serve")
    """
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True
    except requests.ConnectionError:
        return False


def format_docs(docs: List[Any]) -> str:
    """Formatea una lista de documentos LangChain para incluir en el prompt.
    
    Extrae el contenido de texto de cada documento y los concatena
    con doble salto de línea como separador.
    
    Args:
        docs (List[Any]): Lista de objetos Document de LangChain,
            cada uno con un atributo `page_content`.
    
    Returns:
        str: String con el contenido de todos los documentos concatenados,
            separados por '\n\n'.
    
    Example:
        >>> from langchain.schema import Document
        >>> docs = [Document(page_content="Texto 1"), Document(page_content="Texto 2")]
        >>> print(format_docs(docs))
        Texto 1
        
        Texto 2
    """
    return "\n\n".join(doc.page_content for doc in docs)

# --- Fábrica de LLMs (LLM Factory) ---

def get_llm(modelo: str, temperature: float, timeout: int) -> Optional[Any]:
    """Factory que crea instancias de LLM según el proveedor configurado.
    
    Implementa el patrón Factory para abstraer la creación de diferentes
    tipos de LLM (Ollama local, Google Gemini, Groq, Together AI).
    
    Args:
        modelo (str): Identificador del modelo a instanciar. Debe existir
            como clave en MODEL_CONFIG. Ejemplos: 'gemini-1.5-flash',
            'mistral:7b', 'deepseek-r1:1.5b'.
        temperature (float): Controla la creatividad/aleatoriedad de las
            respuestas. Rango: 0.0 (determinístico) a 1.0 (máximo aleatorio).
        timeout (int): Tiempo máximo de espera en segundos para la respuesta
            del modelo. Solo aplica a algunos proveedores.
    
    Returns:
        Optional[Any]: Instancia del LLM configurado (ChatGoogleGenerativeAI,
            ChatOllama, ChatGroq, o Together), o None si hay error en la
            configuración o el proveedor no está disponible.
    
    Raises:
        Muestra errores en la UI de Streamlit en lugar de lanzar excepciones:
        - Si falta la API key requerida
        - Si Ollama no está ejecutándose
        - Si el proveedor no está soportado
    
    Example:
        >>> llm = get_llm("gemini-1.5-flash", temperature=0.2, timeout=120)
        >>> if llm:
        ...     response = llm.invoke("¿Qué es un quaternión?")
    
    Note:
        Las API keys deben estar configuradas en `.streamlit/secrets.toml`.
    """
    config = MODEL_CONFIG.get(modelo, {})
    provider = config.get("provider")

    if provider == "google":
        if 'GOOGLE_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Google en .streamlit/secrets.toml.")
            return None
        return ChatGoogleGenerativeAI(model=modelo.split('/')[-1], api_key=st.secrets["GOOGLE_API_KEY"], temperature=temperature)
    
    elif provider == "ollama":
        if not verificar_ollama():
            st.error("🚨 Ollama no está ejecutándose. Inicia el servicio de Ollama para usar este modelo.")
            return None
        return ChatOllama(model=modelo, temperature=temperature, timeout=timeout)
        
    elif provider == "groq":
        if 'GROQ_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Groq en .streamlit/secrets.toml.")
            return None
        return ChatGroq(api_key=st.secrets["GROQ_API_KEY"], model=modelo.split('/')[-1], temperature=temperature)

    elif provider == "together":
        if 'TOGETHER_API_KEY' not in st.secrets:
            st.error("🚨 Falta la API Key de Together AI en .streamlit/secrets.toml.")
            return None
        return Together(model=modelo, api_key=st.secrets["TOGETHER_API_KEY"], temperature=temperature)
        
    else:
        st.error(f"🚨 Proveedor '{provider}' para el modelo '{modelo}' no está configurado.")
        return None

# --- Funciones de la Interfaz de Usuario ---

def render_sidebar() -> tuple[str, int, float, int]:
    """Renderiza la barra lateral con opciones de configuración del usuario.
    
    Crea todos los widgets de configuración en el sidebar de Streamlit:
    selector de modelo, número de documentos, temperatura y timeout.
    
    Args:
        None
    
    Returns:
        tuple[str, int, float, int]: Tupla con:
            - modelo_seleccionado (str): ID del modelo LLM elegido
            - chunk_size (int): Número de documentos a recuperar (3-10)
            - temperature (float): Nivel de creatividad del LLM (0.0-1.0)
            - timeout (int): Timeout en segundos (30-300)
    
    Example:
        >>> modelo, chunks, temp, timeout = render_sidebar()
        >>> print(f"Usando {modelo} con {chunks} documentos")
    """
    st.sidebar.header("⚙️ Configuración")
    
    modelo_seleccionado = st.sidebar.selectbox(
        "Selecciona el modelo:",
        list(MODEL_CONFIG.keys()),
        index=0
    )
    
    assert modelo_seleccionado is not None, "selectbox no debería devolver None con las opciones dadas"

    st.sidebar.info(MODEL_CONFIG[modelo_seleccionado]["info"])

    with st.sidebar.expander("🔧 Configuración Avanzada"):
        chunk_size = st.slider("Documentos a consultar", 3, 10, 5)
        temperature = st.slider("Creatividad", 0.0, 1.0, 0.2)
        timeout = st.slider("Timeout (segundos)", 30, 300, 120)
        
    return modelo_seleccionado, chunk_size, temperature, timeout

# --- Flujo Principal de la Aplicación ---

def main():
    st.title("Asistente de Investigación INAOE 🤖")
    st.write("Hazme preguntas sobre los documentos del INAOE y te ayudaré a encontrar la información.")

    modelo_sel, chunk_size, temp, timeout = render_sidebar()

    db = cargar_base_datos()
    if db is None:
        return # Detiene la ejecución si la base de datos no se carga
        
    llm = get_llm(modelo_sel, temp, timeout)
    if llm is None:
        return # Detiene la ejecución si el modelo no se puede configurar

    try:
        # Crear el retriever - validar que db no sea None
        if db is None:
            st.error("❌ Error: La base de datos no se pudo cargar correctamente.")
            return
        retriever = db.as_retriever(search_kwargs={"k": chunk_size})
        
        # Crear el prompt template
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
        
        # Crear la nueva cadena RAG con LCEL
        def create_rag_chain():
            def rag_invoke(question):
                # Obtener documentos relevantes
                docs = retriever.get_relevant_documents(question)
                context = format_docs(docs)

                # Si no hay contexto local, intentamos fallback a Internet
                contexto_web = ""
                if not context or len(context.strip()) < 50:
                    resultados_web = buscar_en_internet(question)
                    contexto_web = "\n\n".join(resultados_web)
                    # Si encontramos algo en la web, lo usamos como contexto alterno
                    if contexto_web and "No se encontraron resultados" not in contexto_web:
                        context = f"[Fuente: Internet]\n{contexto_web}"
                
                # Crear el prompt
                formatted_prompt = prompt.format(context=context, question=question)
                
                # Obtener respuesta del LLM
                if llm is None:
                    return {"context": context, "question": question, "answer": "Error: LLM no disponible"}
                response = llm.invoke(formatted_prompt)
                # Convertir la respuesta a string si es necesario
                if hasattr(response, 'content'):
                    answer = response.content
                else:
                    answer = str(response)
                
                return {
                    "context": context,
                    "question": question,
                    "answer": answer
                }
            return rag_invoke
        
        rag_chain_with_source = create_rag_chain()
    except Exception as e:
        st.error(f"Error al crear la cadena de QA: {e}")
        return

    st.markdown("---")
    if 'pregunta' not in st.session_state:
        st.session_state.pregunta = ""

    pregunta = st.text_input("🤔 ¿Qué te gustaría saber?", key="pregunta_input")

    col1, col2, _ = st.columns([1, 1, 3])
    buscar_presionado = col1.button("🔍 Buscar respuesta", type="primary")
    if col2.button("🧹 Limpiar"):
        st.session_state.pregunta_input = ""
        st.rerun()

    if buscar_presionado and pregunta:
        with st.spinner(f"🤖 Buscando respuesta con {modelo_sel}..."):
            start_time = time.time()
            try:
                # Invocación simplificada con la nueva cadena LCEL
                result = rag_chain_with_source(pregunta)
                end_time = time.time()

                st.markdown("### 📝 Respuesta:")
                st.write(result.get("answer", "No se pudo generar una respuesta."))
                
                st.metric("⏱️ Tiempo de respuesta", f"{end_time - start_time:.2f} segundos")

                # Mostrar fuentes consultadas
                if result.get("context") and "No se encontró información relevante" not in result.get("answer", ""):
                    with st.expander("📚 Ver fuentes consultadas"):
                        st.write(result.get("context", ""))

            except Exception as e:
                st.error(f"❌ Error al generar la respuesta: {e}")

if __name__ == "__main__":
    main()