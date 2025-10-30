"""
Utilidades para el proyecto RAG INAOE
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_configuracion() -> Dict[str, Any]:
    """
    Verifica la configuración del proyecto y retorna el estado.
    """
    config: Dict[str, Any] = {
        "base_datos_existe": False,
        "ollama_disponible": False,
        "api_keys_configuradas": False,
        "errores": []
    }
    
    # Verificar base de datos
    ruta_proyecto = Path(__file__).resolve().parent.parent
    ruta_db = ruta_proyecto / "indice_faiss"
    
    if ruta_db.exists() and (ruta_db / "index.faiss").exists():
        config["base_datos_existe"] = True
    else:
        config["errores"].append("Base de datos no encontrada. Ejecuta: python procesar_docs.py")
    
    # Verificar Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            config["ollama_disponible"] = True
    except:
        config["errores"].append("Ollama no está ejecutándose. Inicia con: ollama serve")
    
    # Verificar API keys (si están en secrets)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            if 'GOOGLE_API_KEY' in st.secrets or 'GROQ_API_KEY' in st.secrets:
                config["api_keys_configuradas"] = True
            else:
                config["errores"].append("API keys no configuradas en .streamlit/secrets.toml")
    except:
        config["errores"].append("No se pudo verificar API keys")
    
    return config

def obtener_info_modelo(modelo: str) -> Dict[str, str]:
    """
    Retorna información detallada sobre un modelo específico.
    """
    info_modelos = {
        "gemini-1.5-flash": {
            "proveedor": "Google",
            "tipo": "API Remota",
            "costo": "Gratis",
            "velocidad": "Rápido",
            "precision": "Alta",
            "requisitos": "API Key de Google"
        },
        "llama3-8b-8192": {
            "proveedor": "Groq",
            "tipo": "API Remota", 
            "costo": "Pago por uso",
            "velocidad": "Muy rápido",
            "precision": "Alta",
            "requisitos": "API Key de Groq"
        },
        "gemma-7b-it": {
            "proveedor": "Groq",
            "tipo": "API Remota",
            "costo": "Pago por uso", 
            "velocidad": "Rápido",
            "precision": "Media-Alta",
            "requisitos": "API Key de Groq"
        },
        "qwen3:4b": {
            "proveedor": "Ollama",
            "tipo": "Local",
            "costo": "Gratis",
            "velocidad": "Lento",
            "precision": "Media",
            "requisitos": "PC potente, Ollama instalado"
        },
        "llama3.2:1b": {
            "proveedor": "Ollama", 
            "tipo": "Local",
            "costo": "Gratis",
            "velocidad": "Rápido",
            "precision": "Media",
            "requisitos": "Ollama instalado"
        }
    }
    
    return info_modelos.get(modelo, {
        "proveedor": "Desconocido",
        "tipo": "Desconocido", 
        "costo": "Desconocido",
        "velocidad": "Desconocido",
        "precision": "Desconocido",
        "requisitos": "Desconocido"
    })

def formatear_tiempo(segundos: float) -> str:
    """
    Formatea el tiempo en segundos a un formato legible.
    """
    if segundos < 60:
        return f"{segundos:.1f}s"
    elif segundos < 3600:
        minutos = int(segundos // 60)
        segs = segundos % 60
        return f"{minutos}m {segs:.1f}s"
    else:
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        return f"{horas}h {minutos}m"

def validar_pregunta(pregunta: str) -> tuple[bool, str]:
    """
    Valida si una pregunta es apropiada para el sistema.
    """
    if not pregunta or len(pregunta.strip()) < 3:
        return False, "La pregunta debe tener al menos 3 caracteres"
    
    if len(pregunta) > 500:
        return False, "La pregunta es demasiado larga (máximo 500 caracteres)"
    
    # Palabras clave que indican preguntas apropiadas
    palabras_clave = [
        "qué", "cuál", "cómo", "dónde", "cuándo", "por qué", "quién",
        "explain", "describe", "what", "how", "where", "when", "why", "who"
    ]
    
    pregunta_lower = pregunta.lower()
    tiene_palabra_clave = any(palabra in pregunta_lower for palabra in palabras_clave)
    
    if not tiene_palabra_clave:
        return False, "La pregunta debe ser una pregunta real (usar qué, cómo, cuál, etc.)"
    
    return True, "Pregunta válida"