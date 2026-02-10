"""Utilidades para el proyecto RAG INAOE.

Este módulo proporciona funciones auxiliares para verificación de configuración,
información de modelos, formateo de tiempo y validación de preguntas del usuario.

Functions:
    verificar_configuracion: Verifica el estado del sistema (DB, Ollama, API keys).
    obtener_info_modelo: Retorna metadatos de un modelo LLM específico.
    formatear_tiempo: Convierte segundos a formato legible (Xm Ys).
    validar_pregunta: Valida si una pregunta es apropiada para el sistema.

Example:
    >>> from utils import verificar_configuracion, validar_pregunta
    >>> config = verificar_configuracion()
    >>> print(config['ollama_disponible'])
    True

Author:
    Proyecto INAOE

Version:
    1.0.0
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verificar_configuracion() -> Dict[str, Any]:
    """Verifica la configuración del proyecto y retorna el estado del sistema.
    
    Realiza verificaciones de salud del sistema incluyendo:
    - Existencia de la base de datos vectorial FAISS
    - Disponibilidad del servicio Ollama en localhost
    - Configuración de API keys en Streamlit secrets
    
    Args:
        None
    
    Returns:
        Dict[str, Any]: Diccionario con el estado del sistema conteniendo:
            - base_datos_existe (bool): True si index.faiss existe
            - ollama_disponible (bool): True si Ollama responde en :11434
            - api_keys_configuradas (bool): True si hay API keys en secrets
            - errores (List[str]): Lista de mensajes de error encontrados
    
    Example:
        >>> config = verificar_configuracion()
        >>> if config['errores']:
        ...     for error in config['errores']:
        ...         print(f"Error: {error}")
        >>> if config['ollama_disponible']:
        ...     print("Ollama está listo para usar")
    
    Note:
        Esta función intenta importar `requests` y `streamlit` dinámicamente
        para evitar dependencias circulares.
    """
    config: Dict[str, Any] = {
        "base_datos_existe": False,
        "ollama_disponible": False,
        "api_keys_configuradas": False,
        "errores": []
    }
    
    # Verificar base de datos FAISS
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
    except Exception:
        config["errores"].append("Ollama no está ejecutándose. Inicia con: ollama serve")
    
    # Verificar API keys en Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            if 'GOOGLE_API_KEY' in st.secrets or 'GROQ_API_KEY' in st.secrets:
                config["api_keys_configuradas"] = True
            else:
                config["errores"].append("API keys no configuradas en .streamlit/secrets.toml")
    except Exception:
        config["errores"].append("No se pudo verificar API keys")
    
    return config


def obtener_info_modelo(modelo: str) -> Dict[str, str]:
    """Retorna información detallada sobre un modelo LLM específico.
    
    Proporciona metadatos útiles para cada modelo soportado incluyendo
    proveedor, tipo de conexión, costos y requisitos de hardware.
    
    Args:
        modelo (str): Identificador del modelo. Ejemplos:
            - 'gemini-1.5-flash'
            - 'llama3-8b-8192'
            - 'qwen3:4b'
    
    Returns:
        Dict[str, str]: Diccionario con información del modelo:
            - proveedor (str): Empresa/servicio (Google, Groq, Ollama)
            - tipo (str): 'API Remota' o 'Local'
            - costo (str): 'Gratis' o 'Pago por uso'
            - velocidad (str): 'Lento', 'Rápido', 'Muy rápido'
            - precision (str): 'Media', 'Alta', 'Media-Alta'
            - requisitos (str): Requisitos de hardware/configuración
            
        Si el modelo no está registrado, retorna valores 'Desconocido'.
    
    Example:
        >>> info = obtener_info_modelo('gemini-1.5-flash')
        >>> print(f"Proveedor: {info['proveedor']}")
        Proveedor: Google
        >>> print(f"Costo: {info['costo']}")
        Costo: Gratis
    """
    info_modelos: Dict[str, Dict[str, str]] = {
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
        },
        "deepseek-r1:1.5b": {
            "proveedor": "Ollama",
            "tipo": "Local",
            "costo": "Gratis",
            "velocidad": "Rápido",
            "precision": "Alta",
            "requisitos": "Ollama instalado, ~2GB RAM"
        },
        "mistral:7b": {
            "proveedor": "Ollama",
            "tipo": "Local",
            "costo": "Gratis",
            "velocidad": "Medio",
            "precision": "Alta",
            "requisitos": "Ollama instalado, 4GB RAM"
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
    """Formatea una duración en segundos a un formato legible por humanos.
    
    Convierte segundos a una representación amigable usando segundos,
    minutos y horas según corresponda.
    
    Args:
        segundos (float): Duración en segundos a formatear.
            Puede ser un número decimal.
    
    Returns:
        str: Tiempo formateado según la duración:
            - < 60s: "X.Xs" (ej: "45.3s")
            - < 1h: "Xm X.Xs" (ej: "2m 5.5s")
            - >= 1h: "Xh Xm" (ej: "1h 30m")
    
    Example:
        >>> formatear_tiempo(45.3)
        '45.3s'
        >>> formatear_tiempo(125.5)
        '2m 5.5s'
        >>> formatear_tiempo(3725)
        '1h 2m'
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


def validar_pregunta(pregunta: str) -> Tuple[bool, str]:
    """Valida si una pregunta es apropiada para el sistema RAG.
    
    Realiza validaciones de longitud y contenido para asegurar que
    la pregunta sea procesable y tenga formato de pregunta real.
    
    Args:
        pregunta (str): Texto de la pregunta a validar.
    
    Returns:
        Tuple[bool, str]: Tupla con:
            - bool: True si la pregunta es válida, False si no
            - str: Mensaje descriptivo del resultado de validación
    
    Validation Rules:
        - Mínimo 3 caracteres
        - Máximo 500 caracteres
        - Debe contener al menos una palabra interrogativa
          (qué, cuál, cómo, dónde, cuándo, por qué, quién)
          o sus equivalentes en inglés
    
    Example:
        >>> es_valida, mensaje = validar_pregunta("¿Qué es un quaternión?")
        >>> print(es_valida)
        True
        >>> print(mensaje)
        Pregunta válida
        
        >>> es_valida, mensaje = validar_pregunta("Hola")
        >>> print(es_valida)
        False
        >>> print(mensaje)
        La pregunta debe ser una pregunta real (usar qué, cómo, cuál, etc.)
    """
    if not pregunta or len(pregunta.strip()) < 3:
        return False, "La pregunta debe tener al menos 3 caracteres"
    
    if len(pregunta) > 500:
        return False, "La pregunta es demasiado larga (máximo 500 caracteres)"
    
    # Palabras clave que indican preguntas apropiadas (español e inglés)
    palabras_clave: List[str] = [
        "qué", "cuál", "cómo", "dónde", "cuándo", "por qué", "quién",
        "explain", "describe", "what", "how", "where", "when", "why", "who"
    ]
    
    pregunta_lower = pregunta.lower()
    tiene_palabra_clave = any(palabra in pregunta_lower for palabra in palabras_clave)
    
    if not tiene_palabra_clave:
        return False, "La pregunta debe ser una pregunta real (usar qué, cómo, cuál, etc.)"
    
    return True, "Pregunta válida"