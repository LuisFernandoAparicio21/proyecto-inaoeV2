# -*- coding: utf-8 -*-
"""Configuración global del Asistente de Investigación INAOE.

Este módulo centraliza toda la configuración del sistema incluyendo:
- Rutas del proyecto
- Configuración de modelos LLM
- Configuración de embeddings
- Variables de entorno

Example:
    from backend.app.core.config import settings, MODEL_CONFIG
    
    print(settings.RUTA_PROYECTO)
    print(MODEL_CONFIG["gemini-1.5-flash"])
"""

from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- Rutas del Proyecto ---
RUTA_PROYECTO = Path(__file__).resolve().parent.parent.parent.parent
RUTA_DATA = RUTA_PROYECTO / "data"
RUTA_DOCUMENTOS = RUTA_DATA / "documentos"
RUTA_INDICE_FAISS = RUTA_DATA / "indice_faiss"
RUTA_MODELS = RUTA_DATA / "models"

# --- Configuración de Modelos LLM ---
MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
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
    "gemini-2.0-flash": {
        "provider": "google", 
        "info": "⚡ API Google - Modelo más reciente y rápido, requiere API key."
    },
    "gemini-1.5-pro": {
        "provider": "google", 
        "info": "✨ API Google - Máxima calidad de razonamiento, más lento y costoso."
    },
}

# --- Configuración de Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Configuración de spaCy y NER ---
SPACY_MODEL = "es_core_news_lg"

# --- Configuración de Procesamiento de Documentos ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


class Settings:
    """Clase de configuración con validación.
    
    Centraliza la configuración del sistema y proporciona métodos
    para validar que todos los recursos necesarios estén disponibles.
    
    Attributes:
        RUTA_PROYECTO: Ruta raíz del proyecto
        RUTA_DATA: Ruta a la carpeta de datos
        RUTA_INDICE_FAISS: Ruta al índice vectorial
        DEBUG: Modo debug activado/desactivado
    """
    
    RUTA_PROYECTO = RUTA_PROYECTO
    RUTA_DATA = RUTA_DATA
    RUTA_DOCUMENTOS = RUTA_DOCUMENTOS
    RUTA_INDICE_FAISS = RUTA_INDICE_FAISS
    RUTA_MODELS = RUTA_MODELS
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validar_rutas(cls) -> bool:
        """Valida que las rutas críticas existan.
        
        Returns:
            bool: True si todas las rutas existen, False si alguna falta.
        """
        rutas_requeridas = [cls.RUTA_DATA, cls.RUTA_DOCUMENTOS]
        for ruta in rutas_requeridas:
            if not ruta.exists():
                return False
        return True


# Instancia global de configuración
settings = Settings()
