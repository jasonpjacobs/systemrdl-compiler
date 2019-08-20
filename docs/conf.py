# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------
base_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
with open(os.path.join(base_dir, "systemrdl", "__about__.py")) as f:
    v_dict = {}
    exec(f.read(), v_dict)
    rdl_version = v_dict['__version__']
    rdl_version_short = ".".join(rdl_version.split('.')[:2])

project = 'SystemRDL Compiler'
copyright = '2019, Alex Mykyta'
author = 'Alex Mykyta'

# The full version, including alpha/beta/rc tags
release = rdl_version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.inheritance_diagram',
    'crate.sphinx.csv',
]


inheritance_graph_attrs = dict(
    #rankdir = "TB",
    #size = '"6.0, 8.0"',
    #fontsize = 14,
    #ratio = 'compress'
)

inheritance_node_attrs = dict(
    #shape='ellipse',
    #fontsize=14,
    #height=0.75,
    color='"#6AB0DE"',
    fillcolor='"#E7F2FA"',
    style='"rounded, filled"'
)

autoclass_content = 'both'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

def setup(app):
    app.add_stylesheet('css/theme_overrides.css')

