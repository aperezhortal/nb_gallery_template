import os
from pathlib import Path
import glob

# -- Path setup --------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader

DOCS_FOLDER = Path(__file__).parent
NOTEBOOKS_FOLDER = DOCS_FOLDER / "notebooks"

# -- Project information -----------------------------------------------------

project = "nb_gallery_template"
copyright = "2021, Andres Perez Hortal"
author = "Andres Perez Hortal"

# -- General configuration ---------------------------------------------------

extensions = [
    "nbsphinx",
    "sphinx.ext.mathjax",
]
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# -- Generate the new index.html using jinja templates -----------------------

notebooks_paths = sorted(
    [
        os.path.relpath(_path, DOCS_FOLDER)
        for _path in glob.glob(str(NOTEBOOKS_FOLDER / "*.ipynb"))
    ]
)

env = Environment(loader=FileSystemLoader(searchpath="templates"))

template = env.get_template("index.rst.jinja2")
template.stream(notebooks_paths=notebooks_paths).dump("index.rst")
