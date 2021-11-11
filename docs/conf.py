import os
from collections import defaultdict, OrderedDict
from pathlib import Path
import glob

# -- Path setup --------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader

DOCS_DIR = Path(__file__).parent
NOTEBOOKS_DIR = DOCS_DIR / "notebooks"
GENERATED_DOCS_DIR = DOCS_DIR / "_generated"

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

######################################################################
# Generate the notebooks TOC trees and rst files using jinja templates

# Discover notebooks
# IMPORTANT: Only 1 level of subdirectories are supported!

# Store the notebooks paths in a dictionary (temporary).
# Each key stores the notebooks paths for each subdirectory.
notebooks_by_folder = defaultdict(list)

# First discover notebooks at the NOTEBOOKS folder level
notebooks_paths_in_subdirs = glob.glob(str(NOTEBOOKS_DIR / "*.ipynb")) + glob.glob(
    str(NOTEBOOKS_DIR / "**/*.ipynb")
)

for _path in notebooks_paths_in_subdirs:
    _path = Path(_path)
    sub_gallery_folder = str(_path.relative_to(NOTEBOOKS_DIR).parent)

    notebooks_by_folder[sub_gallery_folder].append(
        os.path.relpath(_path, GENERATED_DOCS_DIR)
    )

# Sort notebooks alphabetically.
for folder, noteboooks in notebooks_by_folder.items():
    notebooks_by_folder[folder] = sorted(noteboooks)

# Sort subfolders alphabetically (subfolder, [list of notebooks paths])
notebooks_by_folder = sorted(notebooks_by_folder.items())

print(notebooks_by_folder)

env = Environment(
    loader=FileSystemLoader(searchpath="templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)

template = env.get_template("gallery_index.rst.jinja2")
template.stream(notebooks_by_folder=notebooks_by_folder).dump(
    str(GENERATED_DOCS_DIR / "gallery_index.rst")
)

template = env.get_template("sub_gallery.rst.jinja2")
os.makedirs(GENERATED_DOCS_DIR, exist_ok=True)
for subfolder, notebooks in notebooks_by_folder:
    if subfolder == ".":
        continue

    title = f"{subfolder.title()} example gallery"
    title = title + "\n" + "=" * len(title)

    template.stream(title=title, notebooks=notebooks).dump(
        str(GENERATED_DOCS_DIR / f"{subfolder}.rst")
    )
