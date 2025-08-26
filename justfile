# Default recipe (shows all available commands)
default:
    @just --list

# Set variables
set dotenv-load

# Define variables
python := "uv run python"

# Install dependencies using uv
install:
    uv pip install -e .
    uv pip install ruff black pytest pytest-django

# Database commands
migrate:
    {{python}} manage.py migrate

makemigrations:
    {{python}} manage.py makemigrations

# Development server
run:
    {{python}} manage.py runserver 0.0.0.0:8000

# Django shell
shell:
    {{python}} manage.py shell

# Testing
test:
    {{python}} -m pytest

# Cleanup commands
clean:
    #!/usr/bin/env sh
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type f -name ".coverage" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name "*.egg" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Code quality
lint:
    uv pip install ruff
    uv run ruff check .

format:
    uv pip install black
    uv run black .

# Django management
superuser:
    {{python}} manage.py createsuperuser

# Generate requirements
requirements:
    uv pip freeze > requirements.txt

# App creation commands
app name:
    {{python}} manage.py startapp {{name}}
    @echo "Created app {{name}} with custom template"

# Combined commands
setup: install migrate superuser

# Development workflow
dev: format lint run
