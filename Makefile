PYTHON_SYS := python3
VENV := .venv
PYTHON := $(VENV)/bin/python
UV := uv
MAIN_DIRECTORY := src


install:
	$(UV) sync

run: install
	$(UV) run python -m $(MAIN_DIRECTORY)

debug:
	$(UV) run python -m pdb $(MAIN_DIRECTORY)/__main__.py

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

.PHONY: install run debug clean lint lint-strict
