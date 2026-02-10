Asistente de Investigación INAOE
=================================

.. image:: https://img.shields.io/badge/Python-3.9+-blue.svg
   :target: https://www.python.org/

.. image:: https://img.shields.io/badge/Streamlit-1.0+-red.svg
   :target: https://streamlit.io/

**Sistema RAG (Retrieval-Augmented Generation) para consulta inteligente de documentos científicos del INAOE.**

Descripción General
-------------------

El Asistente de Investigación INAOE es una aplicación web que permite a los investigadores consultar documentos científicos utilizando inteligencia artificial. Combina:

* **Búsqueda Semántica**: FAISS con embeddings de HuggingFace
* **Múltiples LLMs**: Ollama (local), Google Gemini, Groq, Together AI
* **Enriquecimiento NLP**: spaCy + BERT Spanish NER
* **Fallback Web**: DuckDuckGo cuando no hay contexto local

.. toctree::
   :maxdepth: 2
   :caption: Guías:

   inicio
   instalacion
   arquitectura
   guias

.. toctree::
   :maxdepth: 2
   :caption: Documentación Técnica:

   documentacion_tecnica

.. toctree::
   :maxdepth: 4
   :caption: API Reference:

   api/modules

Índices y Tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
