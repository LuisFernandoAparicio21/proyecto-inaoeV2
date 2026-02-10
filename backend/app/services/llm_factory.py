# -*- coding: utf-8 -*-
"""Factory de modelos LLM para el Asistente de Investigación INAOE.

Este módulo implementa el patrón Factory para crear instancias de diferentes
proveedores de LLM de forma abstracta y configurable.

Proveedores soportados:
    - Ollama (modelos locales)
    - Google Gemini
    - Groq
    - Together AI

Example:
    from backend.app.services.llm_factory import LLMFactory
    
    factory = LLMFactory()
    llm = factory.crear_llm("gemini-1.5-flash", temperature=0.2)
"""

from typing import Any, Optional, Dict
import requests
import logging

from backend.app.core.config import MODEL_CONFIG

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory para crear instancias de LLM según el proveedor configurado.
    
    Implementa el patrón Factory para abstraer la creación de diferentes
    tipos de LLM (Ollama local, Google Gemini, Groq, Together AI).
    
    Attributes:
        api_keys: Diccionario con las API keys de cada proveedor
    
    Example:
        >>> factory = LLMFactory(api_keys={"GOOGLE_API_KEY": "..."})
        >>> llm = factory.crear_llm("gemini-1.5-flash")
        >>> response = llm.invoke("¿Qué es un quaternión?")
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Inicializa el factory con las API keys disponibles.
        
        Args:
            api_keys: Diccionario con las API keys. Claves esperadas:
                - GOOGLE_API_KEY
                - GROQ_API_KEY
                - TOGETHER_API_KEY
        """
        self.api_keys = api_keys or {}
        self._ollama_disponible: Optional[bool] = None
    
    def verificar_ollama(self) -> bool:
        """Verifica si el servicio de Ollama está activo en localhost.
        
        Returns:
            bool: True si Ollama responde correctamente
        """
        if self._ollama_disponible is not None:
            return self._ollama_disponible
        
        try:
            requests.get("http://localhost:11434", timeout=3)
            self._ollama_disponible = True
        except requests.ConnectionError:
            self._ollama_disponible = False
        
        return self._ollama_disponible
    
    def crear_llm(
        self,
        modelo: str,
        temperature: float = 0.2,
        timeout: int = 120
    ) -> Optional[Any]:
        """Crea una instancia de LLM según el proveedor configurado.
        
        Args:
            modelo: Identificador del modelo (debe existir en MODEL_CONFIG)
            temperature: Controla la creatividad (0.0-1.0)
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            Instancia del LLM configurado o None si hay error
        
        Raises:
            ValueError: Si el modelo no está configurado
        """
        config = MODEL_CONFIG.get(modelo)
        if not config:
            raise ValueError(f"Modelo '{modelo}' no encontrado en MODEL_CONFIG")
        
        provider = config.get("provider")
        
        if provider == "google":
            return self._crear_google(modelo, temperature)
        elif provider == "ollama":
            return self._crear_ollama(modelo, temperature, timeout)
        elif provider == "groq":
            return self._crear_groq(modelo, temperature)
        elif provider == "together":
            return self._crear_together(modelo, temperature)
        else:
            logger.error(f"Proveedor '{provider}' no soportado")
            return None
    
    def _crear_google(self, modelo: str, temperature: float) -> Optional[Any]:
        """Crea instancia de Google Gemini."""
        api_key = self.api_keys.get("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Falta GOOGLE_API_KEY")
            return None
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=modelo.split('/')[-1],
                api_key=api_key,
                temperature=temperature
            )
        except ImportError:
            logger.error("langchain_google_genai no instalado")
            return None
    
    def _crear_ollama(self, modelo: str, temperature: float, timeout: int) -> Optional[Any]:
        """Crea instancia de Ollama local."""
        if not self.verificar_ollama():
            logger.error("Ollama no está ejecutándose")
            return None
        
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=modelo,
                temperature=temperature,
                timeout=timeout
            )
        except ImportError:
            logger.error("langchain_ollama no instalado")
            return None
    
    def _crear_groq(self, modelo: str, temperature: float) -> Optional[Any]:
        """Crea instancia de Groq."""
        api_key = self.api_keys.get("GROQ_API_KEY")
        if not api_key:
            logger.error("Falta GROQ_API_KEY")
            return None
        
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=api_key,
                model=modelo.split('/')[-1],
                temperature=temperature
            )
        except ImportError:
            logger.error("langchain_groq no instalado")
            return None
    
    def _crear_together(self, modelo: str, temperature: float) -> Optional[Any]:
        """Crea instancia de Together AI."""
        api_key = self.api_keys.get("TOGETHER_API_KEY")
        if not api_key:
            logger.error("Falta TOGETHER_API_KEY")
            return None
        
        try:
            from langchain_together import Together
            return Together(
                model=modelo,
                api_key=api_key,
                temperature=temperature
            )
        except ImportError:
            logger.error("langchain_together no instalado")
            return None
    
    def listar_modelos_disponibles(self) -> Dict[str, Dict[str, Any]]:
        """Lista los modelos disponibles según las API keys configuradas.
        
        Returns:
            Dict con modelos y su información, solo los que tienen
            credenciales configuradas.
        """
        disponibles = {}
        
        for modelo, config in MODEL_CONFIG.items():
            provider = config.get("provider")
            
            if provider == "ollama" and self.verificar_ollama():
                disponibles[modelo] = config
            elif provider == "google" and self.api_keys.get("GOOGLE_API_KEY"):
                disponibles[modelo] = config
            elif provider == "groq" and self.api_keys.get("GROQ_API_KEY"):
                disponibles[modelo] = config
            elif provider == "together" and self.api_keys.get("TOGETHER_API_KEY"):
                disponibles[modelo] = config
        
        return disponibles
