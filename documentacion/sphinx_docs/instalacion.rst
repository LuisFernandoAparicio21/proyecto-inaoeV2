Instalación Detallada
=====================

Requisitos del Sistema
----------------------

Hardware
^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Componente
     - Mínimo
     - Recomendado
   * - RAM
     - 4GB
     - 8GB+
   * - Espacio en disco
     - 5GB
     - 10GB
   * - GPU
     - No requerida
     - NVIDIA CUDA (opcional)

Software
^^^^^^^^

* Python 3.9, 3.10, 3.11 o 3.12
* pip (gestor de paquetes)
* Git (opcional, para clonar)

Instalación Paso a Paso
-----------------------

1. Clonar el Repositorio
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone <repository-url>
   cd proyecto_rag_inaoe

2. Crear Entorno Virtual
^^^^^^^^^^^^^^^^^^^^^^^^

**Windows:**

.. code-block:: powershell

   python -m venv venv
   .\venv\Scripts\activate

**Linux/Mac:**

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

3. Instalar Dependencias
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install -r requirements.txt

4. Descargar Modelo spaCy
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python -m spacy download es_core_news_lg

5. Instalar Ollama (Opcional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para modelos locales, descarga Ollama de https://ollama.ai

.. code-block:: bash

   # Descargar modelos
   ollama pull mistral:7b
   ollama pull deepseek-r1:1.5b

Verificación de Instalación
---------------------------

.. code-block:: python

   from utils import verificar_configuracion
   
   config = verificar_configuracion()
   print("Base de datos:", "✅" if config["base_datos_existe"] else "❌")
   print("Ollama:", "✅" if config["ollama_disponible"] else "❌")
   print("API Keys:", "✅" if config["api_keys_configuradas"] else "❌")

Solución de Problemas
---------------------

Error: "No module named 'langchain'"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install --upgrade pip
   pip install -r requirements.txt

Error: "spacy model not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python -m spacy download es_core_news_lg

Error: "CUDA out of memory"
^^^^^^^^^^^^^^^^^^^^^^^^^^^

El sistema usa CPU automáticamente. Para forzar CPU:

.. code-block:: python

   # En app.py, línea del device
   device = 'cpu'  # En lugar de 'cuda'
