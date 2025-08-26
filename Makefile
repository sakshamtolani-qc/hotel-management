.PHONY: install migrate makemigrations run shell test clean lint format

# Default Python interpreter
PYTHON = uv run python

# Django management commands
MANAGE = $(PYTHON) manage.py

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies using uv"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make run           - Run development server"
	@echo "  make shell         - Open Django shell"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Remove Python file artifacts"
	@echo "  make lint          - Run code linting (ruff)"
	@echo "  make format        - Format code (black)"
	@echo "  make superuser     - Create a superuser"
	@echo "  make requirements  - Generate requirements.txt"

install:
	uv pip install -e .
	uv pip install ruff black pytest pytest-django

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

run:
	$(MANAGE) runserver 0.0.0.0:8000

shell:
	$(MANAGE) shell

test:
	$(PYTHON) -m pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +

lint:
	uv pip install ruff
	uv run ruff check .

format:
	uv pip install black
	uv run black .

superuser:
	$(MANAGE) createsuperuser

requirements:
	uv pip freeze > requirements.txt

# App-specific commands
app-billing:
	$(MANAGE) startapp billing

app-rooms:
	$(MANAGE) startapp rooms

app-reservations:
	$(MANAGE) startapp reservations

app-users:
	$(MANAGE) startapp users

# Combined commands
setup: install migrate superuser

# Development workflow
dev: format lint run
