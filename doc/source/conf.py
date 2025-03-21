"""Sphinx documentation configuration file."""

from datetime import datetime
import os

from ansys_sphinx_theme import get_version_match

from ansys.hps.data_transfer.client import __version__

# Project information
project = "PyHPS Data Transfer"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "https://hps.docs.pyansys.com")
switcher_version = get_version_match(__version__)

# The short X.Y version
release = version = __version__

# Select desired logo, theme, and declare the html title
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "hps-data-transfer-client"

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys-internal/hps-data-transfer-client/",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
    "logo": "pyansys",
}

# Sphinx extensions
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_jinja",
    "numpydoc",
    "ansys_sphinx_theme.extension.autoapi",
    "sphinx_gallery.gen_gallery",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

nbsphinx_execute = "always"
sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": ["../../examples"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples"],
    # Pattern to search for example files
    "filename_pattern": r".*\.py",
    "run_stale_examples": False,         # Do not re-run examples
    "plot_gallery": False,
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created in
    "doc_module": "ansys-hps-data-transfer-client",
    "ignore_pattern": "flycheck*",
    "thumbnail_size": (350, 350),
    "remove_config_comments": True,
    "show_signature": False,
}


# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    #"scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "numpy": ("https://numpy.org/devdocs", None),
    #"matplotlib": ("https://matplotlib.org/stable", None),
    #"pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    #"pyvista": ("https://docs.pyvista.org/", None),
    #"grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    #"GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    # "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}


autoapi_type = "python"
autoapi_dirs = ["../../src"]
autoapi_generate_api_docs = True
autoapi_root = "api"
autoapi_keep_files = True

# Configuration for Sphinx autoapi
suppress_warnings = [
    "autoapi.duplicate_object",
    "design.grid",
    "docutils",
    "toc.not_readable",
    "toc.not_included",
    "toc.excluded",
    "ref.python",
    "design.fa-build",
]


# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"


# Keep these while the repository is private
linkcheck_ignore = [
    "https://github.com/ansys-internal/hps-data-transfer-client//*",
    "https://hps.docs.pyansys.com/version/stable/*",
    "https://pypi.org/project/ansys-hps-data-transfer-client",
]

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(f"https://github.com/ansys/ansys.hps.data_transfer_client/releases/tag/v{__version__}")

# Examples gallery customization
nbsphinx_execute = "always"

# -- Declare the Jinja context -----------------------------------------------
exclude_patterns = [
    "examples/**/*.txt",
    "api/client/__version__/index.rst",
]

BUILD_API = True
if not BUILD_API:
    exclude_patterns.append("autoapi")

BUILD_EXAMPLES = True
if not BUILD_EXAMPLES:
    exclude_patterns.append("examples/**")
    exclude_patterns.append("examples.rst")

jinja_contexts = {
    "main_toctree": {
        "build_api": BUILD_API,
        "build_examples": BUILD_EXAMPLES,
    }
}


def prepare_jinja_env(jinja_env) -> None:
    """Customize the jinja env.

    Notes
    -----
    See https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment

    """
    jinja_env.globals["project_name"] = project


autoapi_prepare_jinja_env = prepare_jinja_env