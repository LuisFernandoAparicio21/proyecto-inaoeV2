# -*- coding: utf-8 -*-
"""Servicio de búsqueda web para el Asistente de Investigación INAOE.

Este módulo proporciona funcionalidad de búsqueda en internet como fallback
cuando la base de datos local no tiene información suficiente.

Example:
    from backend.app.services.search_service import SearchService
    
    service = SearchService()
    resultados = service.buscar("quaterniones rotación")
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Servicio de búsqueda web usando DuckDuckGo.
    
    Proporciona búsqueda en internet como fallback cuando el contexto
    local de la base de datos FAISS es insuficiente.
    
    Example:
        >>> service = SearchService()
        >>> resultados = service.buscar("telescopio espacial Webb")
        >>> for r in resultados:
        ...     print(r)
    """
    
    def __init__(self, max_resultados_default: int = 5):
        """Inicializa el servicio de búsqueda.
        
        Args:
            max_resultados_default: Número máximo de resultados por defecto
        """
        self.max_resultados_default = max_resultados_default
        self._ddgs_disponible: bool | None = None
    
    def _verificar_ddgs(self) -> bool:
        """Verifica si DuckDuckGo Search está disponible."""
        if self._ddgs_disponible is not None:
            return self._ddgs_disponible
        
        try:
            from duckduckgo_search import DDGS
            self._ddgs_disponible = True
        except ImportError:
            self._ddgs_disponible = False
            logger.warning("duckduckgo-search no instalado")
        
        return self._ddgs_disponible
    
    def buscar(
        self,
        consulta: str,
        max_resultados: int | None = None
    ) -> List[str]:
        """Realiza una búsqueda web usando DuckDuckGo.
        
        Args:
            consulta: Texto de búsqueda
            max_resultados: Número máximo de resultados (opcional)
        
        Returns:
            Lista de strings formateados con título, resumen y URL
        
        Example:
            >>> resultados = service.buscar("ondas gravitacionales LIGO")
            >>> print(resultados[0])
            Título: LIGO detecta ondas gravitacionales
            Resumen: El observatorio LIGO...
            Fuente: https://...
        """
        if not self._verificar_ddgs():
            return ["[Búsqueda web deshabilitada] duckduckgo-search no instalado"]
        
        max_res = max_resultados or self.max_resultados_default
        
        try:
            from duckduckgo_search import DDGS
            
            resultados = []
            with DDGS() as ddgs:
                for item in ddgs.text(
                    consulta,
                    region="wt-wt",
                    safesearch="moderate",
                    max_results=max_res
                ):
                    titulo = item.get("title", "")
                    cuerpo = item.get("body", "")
                    link = item.get("href", "")
                    resultados.append(
                        f"Título: {titulo}\nResumen: {cuerpo}\nFuente: {link}"
                    )
            
            return resultados if resultados else [
                "No se encontraron resultados web relevantes."
            ]
            
        except Exception as e:
            logger.error(f"Error en búsqueda web: {e}")
            return [f"Error en búsqueda web: {e}"]
    
    def buscar_academico(
        self,
        consulta: str,
        max_resultados: int = 5
    ) -> List[str]:
        """Realiza búsqueda enfocada en fuentes académicas.
        
        Agrega términos de búsqueda para priorizar fuentes académicas
        como arXiv, Google Scholar, ResearchGate, etc.
        
        Args:
            consulta: Texto de búsqueda
            max_resultados: Número máximo de resultados
        
        Returns:
            Lista de resultados de fuentes académicas
        """
        consulta_academica = f"{consulta} site:arxiv.org OR site:researchgate.net OR site:scholar.google.com"
        return self.buscar(consulta_academica, max_resultados)
