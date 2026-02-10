# -*- coding: utf-8 -*-
"""Rutas de la API REST del Asistente INAOE.

Define los endpoints para consultas RAG y gestión del sistema.

Example:
    POST /api/v1/query
    {
        "pregunta": "¿Qué es un quaternión?",
        "modelo": "gemini-1.5-flash",
        "num_docs": 5
    }
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os

from backend.app.services.rag_service import RAGService
from backend.app.db.vector_store import VectorStoreService

router = APIRouter()


# --- Schemas ---

class QueryRequest(BaseModel):
    """Request para consulta RAG."""
    pregunta: str = Field(..., min_length=3, description="Pregunta del usuario")
    modelo: str = Field(default="gemini-1.5-flash", description="Modelo LLM a usar")
    num_docs: int = Field(default=5, ge=1, le=20, description="Documentos a consultar")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    timeout: int = Field(default=120, ge=30, le=600)


class QueryResponse(BaseModel):
    """Response de consulta RAG."""
    respuesta: str
    fuentes: List[Dict[str, Any]]
    modelo_usado: str
    num_docs_consultados: int


class SearchRequest(BaseModel):
    """Request para búsqueda de documentos."""
    query: str = Field(..., min_length=3)
    num_docs: int = Field(default=5, ge=1, le=20)


class DocumentResult(BaseModel):
    """Resultado de búsqueda de documento."""
    content: str
    source: str
    page: Any


# --- Dependencias ---

def get_api_keys() -> Dict[str, str]:
    """Obtiene las API keys del entorno."""
    keys = {}
    if os.getenv("GOOGLE_API_KEY"):
        keys["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    if os.getenv("GROQ_API_KEY"):
        keys["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    if os.getenv("TOGETHER_API_KEY"):
        keys["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")
    return keys


# --- Endpoints ---

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Realiza una consulta RAG completa.
    
    Busca en la base de datos de documentos y genera una respuesta
    usando el modelo LLM especificado.
    """
    try:
        api_keys = get_api_keys()
        service = RAGService(api_keys=api_keys)
        
        respuesta, fuentes = service.consultar(
            pregunta=request.pregunta,
            modelo=request.modelo,
            num_docs=request.num_docs,
            temperature=request.temperature,
            timeout=request.timeout,
        )
        
        return QueryResponse(
            respuesta=respuesta,
            fuentes=fuentes,
            modelo_usado=request.modelo,
            num_docs_consultados=request.num_docs,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")


@router.post("/search", response_model=List[DocumentResult])
async def search_documents(request: SearchRequest):
    """Busca documentos sin generar respuesta.
    
    Útil para previsualizar los documentos que se usarían
    para responder una consulta.
    """
    try:
        api_keys = get_api_keys()
        service = RAGService(api_keys=api_keys)
        
        docs = service.buscar_documentos(
            query=request.query,
            num_docs=request.num_docs,
        )
        
        return [DocumentResult(**doc) for doc in docs]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {e}")


@router.get("/stats")
async def get_stats():
    """Obtiene estadísticas de la base de datos."""
    try:
        vs = VectorStoreService()
        stats = vs.obtener_estadisticas()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """Lista los modelos LLM disponibles."""
    from backend.app.core.config import MODEL_CONFIG
    return MODEL_CONFIG
