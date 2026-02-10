# -*- coding: utf-8 -*-
"""Punto de entrada principal del backend FastAPI.

Este módulo configura la aplicación FastAPI y expone los endpoints
de la API REST del Asistente INAOE.

Example:
    Para ejecutar el servidor:
    
    $ cd backend
    $ uvicorn app.main:app --reload

Author:
    Proyecto INAOE
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.api.routes import router as api_router

# Crear aplicación FastAPI
app = FastAPI(
    title="Asistente de Investigación INAOE API",
    description="API REST para el sistema RAG de consulta de documentos científicos",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint raíz con información del servicio."""
    return {
        "service": "Asistente INAOE API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check para kubernetes/docker."""
    return {
        "status": "healthy",
        "database": settings.RUTA_INDICE_FAISS.exists(),
    }
