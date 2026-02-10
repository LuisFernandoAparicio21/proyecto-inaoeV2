# -*- coding: utf-8 -*-
"""Servicio de base de datos vectorial FAISS para el Asistente INAOE.

Este módulo maneja la conexión y operaciones con la base de datos
vectorial FAISS que almacena los embeddings de los documentos.

Example:
    from backend.app.db.vector_store import VectorStoreService
    
    service = VectorStoreService()
    db = service.cargar()
    docs = db.similarity_search("ondas gravitacionales", k=5)
"""

from typing import Optional, Any
from pathlib import Path
import logging

import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from backend.app.core.config import settings, EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Servicio para gestionar la base de datos vectorial FAISS.
    
    Proporciona métodos para cargar, consultar y mantener la base
    de datos de embeddings de documentos.
    
    Attributes:
        ruta_db: Ruta al directorio del índice FAISS
        embeddings: Modelo de embeddings cargado
    
    Example:
        >>> service = VectorStoreService()
        >>> db = service.cargar()
        >>> if db:
        ...     docs = db.similarity_search("quaterniones", k=3)
    """
    
    def __init__(self, ruta_db: Optional[Path] = None):
        """Inicializa el servicio de base de datos vectorial.
        
        Args:
            ruta_db: Ruta al índice FAISS (default: settings.RUTA_INDICE_FAISS)
        """
        self.ruta_db = ruta_db or settings.RUTA_INDICE_FAISS
        self._db: Optional[FAISS] = None
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
    
    def _crear_embeddings(self) -> HuggingFaceEmbeddings:
        """Crea el modelo de embeddings.
        
        Returns:
            Instancia de HuggingFaceEmbeddings configurada
        """
        if self._embeddings is not None:
            return self._embeddings
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Creando embeddings en dispositivo: {device}")
        
        self._embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': device},
            cache_folder=str(settings.RUTA_MODELS),
            encode_kwargs={'normalize_embeddings': True}
        )
        
        return self._embeddings
    
    def cargar(self, force_reload: bool = False) -> Optional[FAISS]:
        """Carga la base de datos vectorial FAISS.
        
        Args:
            force_reload: Si True, recarga aunque ya esté en memoria
        
        Returns:
            Instancia de FAISS cargada o None si hay error
        """
        if self._db is not None and not force_reload:
            return self._db
        
        if not self.ruta_db.exists():
            logger.error(f"No se encontró la base de datos en: {self.ruta_db}")
            return None
        
        try:
            embeddings = self._crear_embeddings()
            self._db = FAISS.load_local(
                str(self.ruta_db),
                embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Base de datos FAISS cargada desde: {self.ruta_db}")
            return self._db
            
        except Exception as e:
            logger.error(f"Error al cargar la base de datos: {e}")
            return None
    
    def existe(self) -> bool:
        """Verifica si la base de datos existe.
        
        Returns:
            True si el directorio del índice existe
        """
        return self.ruta_db.exists()
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas de la base de datos.
        
        Returns:
            Diccionario con número de vectores y dimensiones
        """
        db = self.cargar()
        if db is None:
            return {"error": "Base de datos no disponible"}
        
        try:
            index = db.index
            return {
                "num_vectores": index.ntotal,
                "dimensiones": index.d,
                "ruta": str(self.ruta_db),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def buscar_similares(
        self,
        query: str,
        k: int = 5
    ) -> list:
        """Busca documentos similares a la consulta.
        
        Args:
            query: Texto de consulta
            k: Número de resultados
        
        Returns:
            Lista de documentos ordenados por similitud
        """
        db = self.cargar()
        if db is None:
            return []
        
        return db.similarity_search(query, k=k)
    
    def buscar_con_scores(
        self,
        query: str,
        k: int = 5
    ) -> list:
        """Busca documentos e incluye scores de similitud.
        
        Args:
            query: Texto de consulta
            k: Número de resultados
        
        Returns:
            Lista de tuplas (documento, score)
        """
        db = self.cargar()
        if db is None:
            return []
        
        return db.similarity_search_with_score(query, k=k)
