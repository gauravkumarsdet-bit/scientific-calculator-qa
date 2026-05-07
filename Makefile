# Convenience entry-points for local development.
# Run `make help` to see all targets.

.DEFAULT_GOAL := help
PYTHON       ?= python3
VENV         ?= venv
VENV_BIN     := $(VENV)/bin
PIP          := $(VENV_BIN)/pip
PYTEST       := $(VENV_BIN)/pytest

.PHONY: help venv install install-dev test smoke functional scientific edge ux \
        lint format clean

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Create local virtual environment
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv ## Install runtime dependencies
	$(PIP) install -r requirements.txt

install-dev: venv ## Install runtime + development dependencies
	$(PIP) install -r requirements-dev.txt

test: ## Run the full test suite
	$(PYTEST)

smoke: ## Run smoke tests only
	$(PYTEST) -m smoke

functional: ## Run functional arithmetic tests
	$(PYTEST) -m functional

scientific: ## Run scientific function tests
	$(PYTEST) -m scientific

edge: ## Run edge-case tests
	$(PYTEST) -m edge

ux: ## Run UX / accessibility tests
	$(PYTEST) -m ux

lint: ## Run flake8 over source and tests
	$(VENV_BIN)/flake8 src tests conftest.py

format: ## Auto-format source with black + isort
	$(VENV_BIN)/black src tests conftest.py
	$(VENV_BIN)/isort src tests conftest.py

clean: ## Remove caches and reports
	rm -rf .pytest_cache reports htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
