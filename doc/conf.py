# -*- coding: utf-8 -*-
#
# ephypype documentation build configuration file, created by
# sphinx-quickstart on Wed Sep  6 04:42:26 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys
# sys.path.insert(0, os.path.abspath('.'))

from datetime import date
import sphinx_gallery  # noqa
from sphinx_gallery.sorting import FileNameSortKey
import sphinx_bootstrap_theme
from visbrain.config import CONFIG

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'ephypype')))
sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'ephypype', 'pipelines')))
sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'ephypype', 'nodes')))
sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'ephypype', 'interfaces', 'mne')))

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'numpydoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx_gallery.gen_gallery'
]

# generate autosummary even if no references
autosummary_generate = True
numpydoc_show_class_members = False 

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'ephypype'
td = date.today()
copyright = u'%s, Neuropycon Developers. Last updated on %s' % (td.year,
                                                                td.isoformat())

author = u'Annalisa Pascarela'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = u'0.4'
# The full version, including alpha/beta/rc tags.
release = u'0.4'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
# language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'navbar_title': 'Ephypype',
    'bootswatch_theme': "flatly",
    'navbar_sidebarrel': False,
    'bootstrap_version': "3",
    'navbar_links': [
        ("Gallery", "auto_examples/index"),
        ("API", "api"),
        ("Tutorials", "tutorials/index"),
        ("Workshop", "auto_workshop/index"),
        ("Github", "https://github.com/neuropycon/ephypype", True),
    ],
    'bootswatch_theme': "united"}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'ephypypedoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'ephypype.tex', u'ephypype Documentation',
     u'Annalisa Pascarela', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'ephypype', u'mne_bids Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'ephypype', u'ephypype Documentation',
     author, 'ephypype', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'python': ('https://docs.python.org/', None),
                       'mne': ('http://martinos.org/mne/stable/', None),
                       'nipype': ('https://nipype.readthedocs.io/en/latest/', None),
                       'mne-connectivity': ('https://mne.tools/mne-connectivity/stable', None)
                       }

##############################################################################
# sphinx-gallery

examples_dirs = ['../examples', 'workshop']  # , '../tutorials'
gallery_dirs = ['auto_examples', 'auto_workshop']  # , 'auto_tutorials'

sphinx_gallery_conf = {
    'examples_dirs': examples_dirs,
    'gallery_dirs': gallery_dirs,
    'filename_pattern': re.escape(os.sep) + 'plot',
    'backreferences_dir': 'generated',
    'within_subsection_order': FileNameSortKey,
    'reference_url': {
        'mne': 'http://mne-tools.github.io/stable/',
        'numpy': 'https://numpy.org/doc/1.23/',
        'scipy': 'https://docs.scipy.org/doc/scipy/reference/',
        'nipype': 'https://nipype.readthedocs.io/en/latest/',
        'ephypype': None,
    }
}
   
# {
#  "nbsphinx-toctree": {
#      "maxdepth": 1
#  }
#}
# nbsphinx_execute = 'never'
# gallery_conf["filename_pattern"] = '^((?!sgskip).)*$'
# gallery_conf["ignore_pattern"]   = '__init__\\.py'


import sys
import os.path as op

path = op.join(op.dirname(__file__), '../examples/')
sys.path.insert(0, path)

CONFIG['MPL_RENDER'] = True
