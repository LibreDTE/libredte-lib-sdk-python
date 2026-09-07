.PHONY: install-dev lint format format-check typecheck test test-live check docs build upload clean

VENV = .venv
VENV_READY = $(VENV)/.installed

$(VENV_READY): pyproject.toml
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e '.[dev]'
	touch $(VENV_READY)

install-dev: $(VENV_READY)

lint: $(VENV_READY)
	$(VENV)/bin/ruff check .

format: $(VENV_READY)
	$(VENV)/bin/ruff format .

format-check: $(VENV_READY)
	$(VENV)/bin/ruff format --check .

typecheck: $(VENV_READY)
	$(VENV)/bin/mypy

test: $(VENV_READY)
	$(VENV)/bin/pytest -v

# Tests de integración: golpean la API real de LibreDTE, sin mocks.
# Excluidos de `test`/`check` a propósito (requieren red, y dependen de
# estado externo que este repo no controla).
test-live: $(VENV_READY)
	$(VENV)/bin/pytest -v -m live

check: lint format-check typecheck test

docs: $(VENV_READY)
	$(VENV)/bin/pip install -e '.[docs]'
	$(VENV)/bin/sphinx-apidoc -o docs libredte_lib_sdk --force --separate
	$(VENV)/bin/sphinx-build -b html docs docs/_build/html

build: $(VENV_READY)
	$(VENV)/bin/python -m build

upload: build
	$(VENV)/bin/twine upload dist/*

clean:
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
