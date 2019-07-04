import sys
import os

# srt.py is in the next directory up
sys.path.insert(0, os.path.abspath(".."))

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx.ext.doctest"]

copyright = "Chris Down"
exclude_patterns = ["_build"]
master_doc = "index"
project = "srt"
pygments_style = "sphinx"
source_suffix = ".rst"
templates_path = ["_templates"]

version = "1.11.0"
release = version

html_static_path = ["_static"]
html_theme = "alabaster"
htmlhelp_basename = "srtdoc"

latex_elements = {}
latex_documents = [("index", "srt.tex", "srt Documentation", "Chris Down", "manual")]

man_pages = [("index", "srt", "srt Documentation", ["Chris Down"], 1)]

texinfo_documents = [
    (
        "index",
        "srt",
        "srt Documentation",
        "Chris Down",
        "srt",
        "One line description of project.",
        "Miscellaneous",
    )
]

intersphinx_mapping = {"python": ("https://docs.python.org/3.5", None)}
