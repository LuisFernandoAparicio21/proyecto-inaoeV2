# -*- coding: utf-8 -*-
"""Servicio principal RAG para el Asistente de Investigación INAOE.

Este módulo implementa la lógica central del sistema RAG (Retrieval-Augmented Generation):
- Búsqueda semántica en la base de datos FAISS
- Generación de respuestas con LLMs
- Formateo de documentos y referencias

Example:
    from backend.app.services.rag_service import RAGService
    
    service = RAGService(api_keys={"GOOGLE_API_KEY": "..."})
    respuesta = service.consultar("¿Qué es un quaternión?")
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
import re

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.app.core.config import settings, MODEL_CONFIG
from backend.app.core.prompts import PROMPT_TEMPLATE, PROMPT_SIN_CONTEXTO
from backend.app.services.llm_factory import LLMFactory
from backend.app.services.search_service import SearchService
from backend.app.db.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

# Patrones para detectar saludos simples
SALUDOS = ["hola", "hello", "hi", "buenos días", "buenas tardes", "buenas noches", "hey", "qué tal", "como estas"]


def limpiar_respuesta_modelo(respuesta: str) -> str:
    """Limpia las etiquetas <think>...</think> de modelos de razonamiento como DeepSeek.
    
    Args:
        respuesta: Respuesta cruda del modelo
    
    Returns:
        Respuesta limpia sin el contenido de razonamiento
    """
    # Eliminar todo el contenido entre <think> y </think>
    respuesta_limpia = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL)
    # Limpiar espacios extra
    respuesta_limpia = respuesta_limpia.strip()
    return respuesta_limpia


def es_saludo_simple(pregunta: str) -> bool:
    """Detecta si la pregunta es un saludo simple.
    
    Args:
        pregunta: Pregunta del usuario
    
    Returns:
        True si es un saludo simple
    """
    pregunta_limpia = pregunta.lower().strip()
    return pregunta_limpia in SALUDOS or len(pregunta_limpia) < 10


class RAGService:
    """Servicio principal de Retrieval-Augmented Generation.
    
    Orquesta la búsqueda semántica, generación de respuestas y formateo
    de documentos para el asistente de investigación.
    
    Attributes:
        llm_factory: Factory para crear instancias de LLM
        search_service: Servicio de búsqueda web
        vector_store: Servicio de base de datos vectorial
    
    Example:
        >>> service = RAGService(api_keys={"GOOGLE_API_KEY": "..."})
        >>> respuesta, fuentes = service.consultar(
        ...     pregunta="¿Qué investigaciones hay sobre ondas gravitacionales?",
        ...     modelo="gemini-1.5-flash",
        ...     num_docs=5
        ... )
        >>> print(respuesta)
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Inicializa el servicio RAG.
        
        Args:
            api_keys: Diccionario con las API keys de los proveedores LLM
        """
        self.api_keys = api_keys or {}
        self.llm_factory = LLMFactory(api_keys=self.api_keys)
        self.search_service = SearchService()
        self.vector_store = VectorStoreService()
        
        # Crear prompt template
        self.prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
    
    @staticmethod
    def format_docs(docs: List[Any]) -> str:
        """Formatea una lista de documentos para incluir en el prompt.
        
        Args:
            docs: Lista de objetos Document de LangChain
        
        Returns:
            String con el contenido concatenado
        """
        return "\n\n".join(doc.page_content for doc in docs)
    
    @staticmethod
    def extraer_fuentes(docs: List[Any]) -> List[Dict[str, Any]]:
        """Extrae metadatos de fuentes de los documentos.
        
        Args:
            docs: Lista de documentos recuperados
        
        Returns:
            Lista de diccionarios con source y page
        """
        fuentes = []
        for doc in docs:
            metadata = doc.metadata
            fuentes.append({
                "source": metadata.get("source", "Desconocido"),
                "page": metadata.get("page", "N/A"),
            })
        return fuentes
    
    def consultar(
        self,
        pregunta: str,
        modelo: str = "gemini-1.5-flash",
        num_docs: int = 5,
        temperature: float = 0.2,
        timeout: int = 120,
        usar_web_fallback: bool = True
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Realiza una consulta RAG completa.
        
        Args:
            pregunta: Pregunta del usuario
            modelo: Modelo LLM a utilizar
            num_docs: Número de documentos a recuperar
            temperature: Temperatura del LLM
            timeout: Timeout en segundos
            usar_web_fallback: Si usar búsqueda web cuando no hay contexto
        
        Returns:
            Tuple con (respuesta_generada, lista_de_fuentes)
        
        Raises:
            ValueError: Si no se puede crear el LLM o cargar la BD
        """
        # Detectar saludos simples y responder directamente
        if es_saludo_simple(pregunta):
            return (
                "¡Hola! Soy el asistente de investigación del INAOE. "
                "Puedo ayudarte a buscar información en los documentos científicos de la institución. "
                "¿En qué puedo ayudarte hoy?",
                []
            )
        
        # Cargar base de datos
        db = self.vector_store.cargar()
        if db is None:
            raise ValueError("No se pudo cargar la base de datos FAISS")
        
        # Crear LLM
        llm = self.llm_factory.crear_llm(modelo, temperature, timeout)
        if llm is None:
            raise ValueError(f"No se pudo crear LLM para modelo: {modelo}")
        
        # Recuperar documentos relevantes
        retriever = db.as_retriever(search_kwargs={"k": num_docs})
        docs = retriever.invoke(pregunta)
        
        # Verificar si hay contexto suficiente
        if not docs or len(docs) == 0:
            if usar_web_fallback:
                return self._responder_sin_contexto(pregunta, llm)
            else:
                return "No se encontró información relevante en la base de datos.", []
        
        # Construir cadena RAG
        rag_chain = (
            RunnableParallel({
                "context": lambda x: self.format_docs(docs),
                "question": RunnablePassthrough()
            })
            | self.prompt
            | llm
            | StrOutputParser()
        )
        
        # Generar respuesta
        respuesta = rag_chain.invoke(pregunta)
        
        # Limpiar respuesta (remover <think>...</think> de DeepSeek)
        respuesta = limpiar_respuesta_modelo(respuesta)
        
        fuentes = self.extraer_fuentes(docs)
        
        return respuesta, fuentes
    
    def _responder_sin_contexto(
        self,
        pregunta: str,
        llm: Any
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Genera respuesta usando búsqueda web cuando no hay contexto local.
        
        Args:
            pregunta: Pregunta del usuario
            llm: Instancia del LLM
        
        Returns:
            Tuple con (respuesta, lista_vacía_de_fuentes)
        """
        # Buscar en internet
        resultados_web = self.search_service.buscar(pregunta)
        web_text = "\n\n".join(resultados_web)
        
        # Crear prompt sin contexto
        prompt = PromptTemplate(
            template=PROMPT_SIN_CONTEXTO,
            input_variables=["question", "web_results"]
        )
        
        chain = prompt | llm | StrOutputParser()
        respuesta = chain.invoke({
            "question": pregunta,
            "web_results": web_text
        })
        
        return respuesta, []
    
    def buscar_documentos(
        self,
        query: str,
        num_docs: int = 5
    ) -> List[Dict[str, Any]]:
        """Busca documentos sin generar respuesta.
        
        Útil para previsualizar los documentos que se usarían
        para responder una consulta.
        
        Args:
            query: Consulta de búsqueda
            num_docs: Número de documentos a retornar
        
        Returns:
            Lista de documentos con contenido y metadatos
        """
        db = self.vector_store.cargar()
        if db is None:
            return []
        
        retriever = db.as_retriever(search_kwargs={"k": num_docs})
        docs = retriever.invoke(query)
        
        return [
            {
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "source": doc.metadata.get("source", "Desconocido"),
                "page": doc.metadata.get("page", "N/A"),
            }
            for doc in docs
        ]
