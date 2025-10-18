import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "DevOps Final - LLM Compose Generator"
copyright = "2025, Tudor Huza"
author = "Tudor Huza"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.viewcode",
]

# Allow parsing of .md files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = ["api/modules.rst"]


autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]


def skip_pydantic(app, what, name, obj, skip, options):
    """
    Skip Pydantic validator methods during Sphinx autodoc generation.

    Args:
        app (sphinx.application.Sphinx): The Sphinx application object.
        what (str): The type of the object which the docstring belongs to 
            (e.g., "module", "class", "method", "function").
        name (str): The name of the object.
        obj (Any): The object itself.
        skip (bool): The default skip decision by autodoc.
        options (dict): The options given to the directive.

    Returns:
        bool: True if the member should be skipped, otherwise returns the
        original `skip` value.
    """
    from pydantic import field_validator  # noqa: F401

    if hasattr(obj, "__pydantic_validator__"):
        return True

    if name in {
        "construct", "copy", "dict", "from_orm", "json", "model_construct",
        "model_copy", "model_dump", "model_dump_json", "model_json_schema",
        "model_parametrized_name", "model_post_init", "model_rebuild",
        "model_validate", "model_validate_json", "model_validate_strings",
        "parse_file", "parse_obj", "parse_raw", "schema", "schema_json",
        "settings_customise_sources", "update_forward_refs", "validate"
    }:
        return True

    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_pydantic)
