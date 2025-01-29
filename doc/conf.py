# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as get_version

release = get_version("ewoksutils")

project = "ewoksutils"
version = ".".join(release.split(".")[:2])
copyright = "2021-2025, ESRF"
author = "ESRF"
docstitle = f"{project} {version}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]
templates_path = ["_templates"]
exclude_patterns = []

always_document_param_types = True

# mermaid does not render when nbsphinx is used
# https://github.com/spatialaudio/nbsphinx/issues/678
nbsphinx_requirejs_path = ""

autosummary_generate = True
autodoc_default_flags = [
    "members",
    "undoc-members",
    "show-inheritance",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = []
html_theme_options = {
    "icon_links": [
        {
            "name": "gitlab",
            "url": "https://gitlab.esrf.fr/workflow/ewoks/ewoksutils",
            "icon": "fa-brands fa-gitlab",
        },
        {
            "name": "pypi",
            "url": "https://pypi.org/project/ewoksutils",
            "icon": "fa-brands fa-python",
        },
    ],
    "footer_start": ["copyright"],
    "footer_end": ["footer_end"],
}
