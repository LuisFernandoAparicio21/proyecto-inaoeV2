Inicio Rápido
=============

Requisitos
----------

* Python 3.9 o superior
* 4GB RAM mínimo (8GB recomendado)
* Ollama instalado (opcional, para modelos locales)

Instalación Rápida
------------------

.. code-block:: bash

   # Clonar repositorio
   git clone <repository-url>
   cd proyecto_rag_inaoe

   # Crear entorno virtual
   python -m venv venv
   .\venv\Scripts\activate  # Windows

   # Instalar dependencias
   pip install -r requirements.txt

   # Descargar modelo spaCy
   python -m spacy download es_core_news_lg

   # Procesar documentos
   cd src
   python procesar_docs.py

   # Ejecutar aplicación
   streamlit run app.py

La aplicación estará disponible en http://localhost:8501

Primer Uso
----------

1. Coloca tus documentos PDF en la carpeta ``documentos/``
2. Ejecuta ``python procesar_docs.py`` para indexarlos
3. Ejecuta ``streamlit run app.py``
4. Selecciona un modelo LLM en el sidebar
5. ¡Haz tu primera pregunta!

Configuración de API Keys
-------------------------

Para usar modelos cloud (Gemini, Groq), crea el archivo ``.streamlit/secrets.toml``:

.. code-block:: toml

   GOOGLE_API_KEY = "tu-api-key-de-google"
   GROQ_API_KEY = "tu-api-key-de-groq"
