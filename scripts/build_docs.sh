#!/usr/bin/env bash
set -e

/bin/rm -rf docs/source/api
uv run python docs/source/generate_api_docs.py
pandoc README.md -f markdown -t rst -o docs/source/README.rst
pandoc usefull_commands.md -f markdown -t rst -o docs/source/usefull_commands.rst
/bin/rm -rf docs/build
uv run sphinx-build -b html docs/source docs/build
