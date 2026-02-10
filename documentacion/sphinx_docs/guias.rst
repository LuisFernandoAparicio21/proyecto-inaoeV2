Guías de Uso
============

Configuración de Modelos LLM
----------------------------

Ollama (Local)
^^^^^^^^^^^^^^

Para usar modelos locales sin internet:

1. Instala Ollama desde https://ollama.ai
2. Descarga el modelo:

.. code-block:: bash

   ollama pull mistral:7b
   # o
   ollama pull deepseek-r1:1.5b

3. Inicia el servicio:

.. code-block:: bash

   ollama serve

Google Gemini
^^^^^^^^^^^^^

1. Obtén una API key en https://makersuite.google.com
2. Agrega al archivo ``.streamlit/secrets.toml``:

.. code-block:: toml

   GOOGLE_API_KEY = "tu-api-key"

Procesamiento de Documentos
---------------------------

Agregar Nuevos Documentos
^^^^^^^^^^^^^^^^^^^^^^^^^

1. Coloca los PDFs en ``documentos/``
2. Ejecuta el pipeline:

.. code-block:: bash

   cd src
   python procesar_docs.py

El sistema detecta automáticamente archivos nuevos o modificados.

Forzar Reprocesamiento
^^^^^^^^^^^^^^^^^^^^^^

Elimina el archivo de registro para reprocesar todo:

.. code-block:: bash

   del processed_files.json
   python procesar_docs.py

Uso de la Interfaz Web
----------------------

Hacer una Consulta
^^^^^^^^^^^^^^^^^^

1. Selecciona el modelo en el sidebar
2. Ajusta parámetros si es necesario:
   - **Documentos**: Cantidad de chunks a recuperar (3-10)
   - **Creatividad**: Temperature del LLM (0.0-1.0)
   - **Timeout**: Tiempo máximo de espera
3. Escribe tu pregunta
4. Haz clic en "Buscar respuesta"

Interpretar Resultados
^^^^^^^^^^^^^^^^^^^^^^

La respuesta incluye:

* **Resumen Ejecutivo**: Respuesta breve
* **Análisis Detallado**: Explicación completa
* **Conclusión**: Implicaciones
* **Fuentes**: Documentos utilizados (con página)

Deployment
----------

Streamlit Cloud
^^^^^^^^^^^^^^^

1. Sube el proyecto a GitHub
2. Conecta en https://share.streamlit.io
3. Configura secrets en el dashboard

.. warning::
   Streamlit Cloud no soporta Ollama. Usa solo APIs cloud.

Docker
^^^^^^

.. code-block:: dockerfile

   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   RUN python -m spacy download es_core_news_lg
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "src/app.py"]

.. code-block:: bash

   docker build -t inaoe-assistant .
   docker run -p 8501:8501 inaoe-assistant
