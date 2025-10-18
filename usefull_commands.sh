# Compile the [requirements.txt](requirements.txt)
uv export -o requirements.txt --no-header --no-hashes

# Lint files with ruff
uv run ruff check
uv run ruff format
uv run ruff clena

# Run pylint
uv run pylint src/devops_final_backend

# Create the rst files for python modules
uv run python docs/source/generate_api_docs.py

# Create the rst files for the README - this requires the pandoc utility to be installed
pandoc README.md -f markdown -t rst -o docs/source/README.rst

# Compile the HTML files
uv run sphinx-build -b html docs/source docs/build