.PHONY: help install uninstall reinstall version run lint format security clear
.DEFAULT_GOAL := help
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?$$', line)
	if match:
		target = match.groups()
		print("%s" % (target))
endef
export PRINT_HELP_PYSCRIPT

$(VENV)/bin/activate: requirements-dev.txt requirements.txt
	@python3.10 -m venv $(VENV)
	@$(PIP) install -U pip
	@$(PIP) install -r requirements-dev.txt

help:
	@python3.10 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

install: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit install
	@$(VENV)/bin/pre-commit install --hook-type commit-msg
	@test -e .env || cp .env.sample .env

uninstall:
	-@$(VENV)/bin/pre-commit uninstall
	@rm -rf $(VENV)

reinstall: uninstall install

version: $(VENV)/bin/activate
	@$(PYTHON) --version
	@$(PIP) --version
	@$(PIP) freeze

run: $(VENV)/bin/activate
	$(PYTHON) -m bot

lint: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit run mypy
	@$(VENV)/bin/pre-commit run ruff

format: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit run black
	@$(VENV)/bin/pre-commit run isort
	@$(VENV)/bin/pre-commit run check-docstring-first
	@$(VENV)/bin/pre-commit run end-of-file-fixer
	@$(VENV)/bin/pre-commit run fix-encoding-pragma
	@$(VENV)/bin/pre-commit run trailing-whitespace

security: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit run bandit
	@$(VENV)/bin/pre-commit run detect-private-key
	@$(VENV)/bin/pre-commit run debug-statements

clear:
	-@rm -fr build/
	-@rm -fr dist/
	-@rm -fr .eggs/
	-@find . -name '*.egg-info' -exec rm -fr {} +
	-@find . -name '*.egg' -exec rm -f {} +
	-@find . -name '*.pyc' -exec rm -f {} +
	-@find . -name '*.pyo' -exec rm -f {} +
	-@find . -name '*~' -exec rm -f {} +
	-@find . -name '__pycache__' -exec rm -fr {} +
	-@rm -fr .tox/
	-@rm -fr .nox/
	-@rm -f .coverage
	-@rm -fr htmlcov/
	-@rm -fr .pytest_cache
	-@rm -fr .mypy_cache
	-@rm -fr .ruff_cache
