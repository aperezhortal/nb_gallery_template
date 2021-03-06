import glob
import os
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

# -- General configuration ----------------------------------------------------

# Documentation root folder
DOCS_DIR = Path(__file__).parent

# Directory with the executed notebooks
NOTEBOOKS_DIR = DOCS_DIR / "notebooks"

# Folder where the notebooks indexes (rst files) are saved.
GENERATED_DOCS_DIR = DOCS_DIR / "_generated"

# Auxiliary repository with the examples notebooks.
# IMPORTANT: The notebooks should be placed in the <aux_project_root>/notebooks folder.
# Only 1 level of subdirectories are supported!
NOTEBOOKS_REPOSITORY = "https://github.com/aperezhortal/nb_gallery_notebooks.git"

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
html_theme = "sphinx_rtd_theme"

# -- Other options -----------------------------------------------------------
nbsphinx_execute = "never"  # Do not execute notebooks


def pull_notebooks(work_dir):
    """Pull the rendered notebooks from an auxiliary repository."""

    # Default to the "latest" branch, containing the latest rendered notebooks.
    rtd_version = os.environ.get("READTHEDOCS_VERSION", "latest")

    if rtd_version == "stable":
        try:
            rtd_version = subprocess.check_output(
                ["git", "describe", "--abbrev=0", "--tags"], universal_newlines=True
            ).strip()
        except subprocess.CalledProcessError:
            rtd_version = "latest"

    print("RTD Version: {}".format(rtd_version))

    cmd = (
        f"git clone {NOTEBOOKS_REPOSITORY} --depth 1 --branch {rtd_version} {work_dir}"
    )
    subprocess.check_output(cmd.split(" "))

    if NOTEBOOKS_DIR.is_dir():
        shutil.rmtree(NOTEBOOKS_DIR)

    shutil.copytree(os.path.join(work_dir, "notebooks"), NOTEBOOKS_DIR)


def generate_notebooks_rst():
    """
    Generate the notebooks TOC trees and rst files using jinja templates.
    """
    from jinja2 import Environment, FileSystemLoader

    ##########################################################
    # 1. Discover notebooks
    # IMPORTANT: Only 1 level of subdirectories are supported!

    # Store the notebooks paths in a dictionary (temporary).
    # Each key stores the notebooks paths for each subdirectory.
    notebooks_by_folder = defaultdict(list)

    # First discover notebooks at the NOTEBOOKS folder level
    notebooks_paths_in_subdirs = glob.glob(
        str(NOTEBOOKS_DIR / "**/*.ipynb"), recursive=True
    )

    for _path in notebooks_paths_in_subdirs:
        _path = Path(_path)
        sub_gallery_folder = str(_path.relative_to(NOTEBOOKS_DIR).parent)

        notebooks_by_folder[sub_gallery_folder].append(
            os.path.relpath(_path, GENERATED_DOCS_DIR)
        )

    ########################################################
    # 2. Sort notebooks alphabetically inside each subfolder
    for folder, noteboooks in notebooks_by_folder.items():
        notebooks_by_folder[folder] = sorted(noteboooks)

    ##########################################################################
    # 3. Sort subfolders alphabetically (subfolder, [list of notebooks paths])
    notebooks_by_folder = sorted(notebooks_by_folder.items())

    env = Environment(
        loader=FileSystemLoader(searchpath="templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    os.makedirs(GENERATED_DOCS_DIR, exist_ok=True)

    ################################################################
    # 4. Generate the rst files for the notebooks documentation page
    template = env.get_template("gallery_index.rst.jinja2")
    template.stream(notebooks_by_folder=notebooks_by_folder).dump(
        str(GENERATED_DOCS_DIR / "gallery_index.rst")
    )

    template = env.get_template("sub_gallery.rst.jinja2")

    for subfolder, notebooks in notebooks_by_folder:
        if subfolder == ".":
            continue

        title = f"{subfolder.title()} example gallery"
        title = title + "\n" + "=" * len(title)

        template.stream(title=title, notebooks=notebooks).dump(
            str(GENERATED_DOCS_DIR / f"{subfolder}.rst")
        )


########################################################################
# Run auxiliary tasks inside a temp folder that is automatically cleaned
with tempfile.TemporaryDirectory() as _work_dir:
    pull_notebooks(_work_dir)
    generate_notebooks_rst()
