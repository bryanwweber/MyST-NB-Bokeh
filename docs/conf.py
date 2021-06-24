# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = "MyST-NB-Bokeh"
copyright = "2021, Bryan Weber"
author = "Bryan Weber"

# The full version, including alpha/beta/rc tags
release = "0.1.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_nb_bokeh",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "special-members": "__init__",
    "undoc-members": True,
}
myst_enable_extensions = [
    "colon_fence",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/3.x", None),
    "myst_nb": ("https://myst-nb.readthedocs.io/en/latest/", None),
    "nbformat": ("https://nbformat.readthedocs.io/en/latest", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "jupyter_execute"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_title = "MyST-NB Bokeh"
html_theme = "sphinx_book_theme"
html_theme_options = {
    "github_url": "https://github.com/bryanwweber/myst_nb_bokeh",
    "repository_url": "https://github.com/bryanwweber/myst_nb_bokeh",
    "repository_branch": "main",
    "use_repository_button": True,
    "use_issues_button": True,
    "home_page_in_toc": True,
    "use_edit_page_button": True,
    "path_to_docs": "docs/",
    "show_navbar_depth": 2,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
