.PHONY: all convert content index listen clean

# Define variables for commands
VENV = venv/bin/activate
PYTHON = python
PAGEFIND = pagefind
PELICAN = pelican
PIP = pip

INSTALL_CMD = source $(VENV) && $(PIP) install -r requirements.txt
CONVERT_CMD = source $(VENV) && $(PYTHON) build_content.py
PELICAN_CMD = source $(VENV) && $(PELICAN) content 
PAGEFIND_CMD = source $(VENV) && $(PYTHON) build_search_index.py
LISTEN_CMD = source $(VENV) && $(PELICAN) --listen -r
CLEANUP_CMD = rm -rf output content/nbimages content/pages && rm -f content/*.md && rm -f *.log

# The default target, runs all steps
all: help

# Display this help message
help:
	@echo "Available commands:"
	@echo "  make help       - Show this help message."
	@echo "  make convert    - Convert sources (notebooks/, posts/) to Markdown in content/."
	@echo "  make content    - Generate content using Pelican."
	@echo "  make index      - Generate the search index using custom Pagefind script (articles only)."
	@echo "  make build      - Run convert, then Pelican content generation and Pagefind indexing."
	@echo "  make listen     - Start a local development server."
	@echo "  make clean      - Clean up build artifacts."

# Convert all sources (notebooks, markdown) to Pelican markdown
convert:
	@echo "Converting sources to markdown..."
	$(CONVERT_CMD)

# Generate content using Pelican
content:
	@echo "Generating Pelican content..."
	$(PELICAN_CMD)

# Generate the search index using Pagefind
index:
	@echo "Generating Pagefind index..."
	$(PAGEFIND_CMD)

# Start the development server
listen:
	@echo "Starting Pelican development server..."
	$(LISTEN_CMD)

# Clean up build artifacts
clean:
	@echo "Cleaning up build artifacts..."
	$(CLEANUP_CMD)

# A special target that runs content generation and indexing
build: convert content index