# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------
# Agregar el directorio src al path para que Sphinx pueda importar los módulos
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
project = 'Asistente de Investigación INAOE'
copyright = '2024, Proyecto INAOE'
author = 'Proyecto INAOE'
release = '1.0.0'
version = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',          # Genera docs desde docstrings
    'sphinx.ext.napoleon',         # Soporte para Google/NumPy docstrings
    'sphinx.ext.viewcode',         # Links al código fuente
    'sphinx.ext.githubpages',      # Soporte para GitHub Pages
    'sphinx.ext.intersphinx',      # Links a otras documentaciones
    'myst_parser',                 # Soporte para Markdown
    'rst2pdf.pdfbuilder',          # Generación de PDF
]

# Configuración de Napoleon (para Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Configuración de autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autodoc_typehints_format = 'short'

# Soporte para archivos Markdown
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# El archivo índice principal
master_doc = 'index'

# Idioma de la documentación
language = 'es'

# Patrones a excluir
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# Tema Read the Docs (profesional)
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Nombre del proyecto en la barra lateral
html_title = "Asistente INAOE - Documentación"
html_short_title = "INAOE Docs"

# Archivos estáticos personalizados
html_static_path = ['_static']

# Logo (opcional)
# html_logo = '_static/logo.png'

# Favicon (opcional)
# html_favicon = '_static/favicon.ico'

# -- Options for LaTeX/PDF output --------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '11pt',
    'preamble': r'''
        \usepackage[utf8]{inputenc}
        \usepackage[spanish]{babel}
    ''',
}

latex_documents = [
    (master_doc, 'AsistenteINAOE.tex', 'Asistente de Investigación INAOE',
     'Proyecto INAOE', 'manual'),
]

# -- Intersphinx configuration -----------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'langchain': ('https://api.python.langchain.com/en/latest/', None),
}
