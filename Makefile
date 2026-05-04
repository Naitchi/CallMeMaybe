PYTHON_SYS := python3
VENV := .venv
PYTHON := $(VENV)/bin/python
UV := $(VENV)/bin/uv
MAIN_SCRIPT := src/main.py

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON_SYS) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install uv
	$(UV) pip install --python $(PYTHON) -e . flake8 mypy

run:
	$(UV) run --python $(PYTHON) python $(MAIN_SCRIPT)

debug:
	$(UV) run --python $(PYTHON) python -m pdb $(MAIN_SCRIPT)

clean:
	rm -rf $(VENV) __pycache__ .mypy_cache .pytest_cache .ruff_cache .coverage
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	find . -type d -name '.ruff_cache' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.pyd' -delete

lint:
	$(UV) run --python $(PYTHON) flake8 .
	$(UV) run --python $(PYTHON) mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run --python $(PYTHON) flake8 .
	$(UV) run --python $(PYTHON) mypy . --strict
