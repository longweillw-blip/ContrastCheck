.PHONY: help venv install install-dev test test-cov lint format clean build upload docs

help:
	@echo "ContrastCheck - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  venv          - Create virtual environment with uv"
	@echo "  install       - Install package in production mode"
	@echo "  install-dev   - Install package with development dependencies"
	@echo "  test          - Run tests with pytest"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  lint          - Run code quality checks (flake8, mypy)"
	@echo "  format        - Format code with black and isort"
	@echo "  clean         - Remove build artifacts and cache files"
	@echo "  build         - Build distribution packages"
	@echo "  upload        - Upload package to PyPI"
	@echo "  docs          - Generate documentation"

venv:
	uv venv --python 3.10
	@echo "Virtual environment created. Activate it with:"
	@echo "  source .venv/bin/activate  (macOS/Linux)"
	@echo "  .venv\\Scripts\\activate     (Windows)"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=contrast_check --cov-report=html --cov-report=term

lint:
	flake8 contrast_check/ tests/
	mypy contrast_check/ --ignore-missing-imports

format:
	black contrast_check/ tests/ examples/
	isort contrast_check/ tests/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

docs:
	@echo "Documentation generation coming soon..."

run-example:
	python examples/simple_usage.py

.DEFAULT_GOAL := help
