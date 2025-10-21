# Usefull comands

## Pre-Commit Hooks

### Install

```sh
uv run pre-commit install && uv run pre-commit install-hooks
```

### Run

```sh
uv run pre-commit run --all-files
```

## Compile the [requirements.txt](requirements.txt)

```sh
uv export -o requirements.txt --no-header --no-hashes
```

## Lint files with ruff

```sh
uv run ruff check
uv run ruff format
uv run ruff clear
```

## Lint files with mypy

```sh
uv run mypy src/devops_final_backend
```

## Lint files with pylint

```sh
uv run pylint src/devops_final_backend
```

## Create the rst files for python modules
```sh
rm -r docs/source/api
uv run python docs/source/generate_api_docs.py
```

## Create the rst files for the README - this requires the pandoc utility to be installed
```sh
pandoc README.md -f markdown -t rst -o docs/source/README.rst
pandoc usefull_commands.md -f markdown -t rst -o docs/source/usefull_commands.rst
```

## Compile the HTML files
```sh
rm -r docs/build
uv run sphinx-build -b html docs/source docs/build
```

## Open file in browser
```sh
xdg-open docs/build/index.html
```
