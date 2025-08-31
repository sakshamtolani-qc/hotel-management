# Default recipe (shows all available commands)
default:
    @just --list

# Set variables
set dotenv-load

# Define variables
python := "uv run python"

# Install dependencies using uv
install:
    #!/usr/bin/env sh
    if [ -f "requirements.txt" ]; then
        uv pip install -r requirements.txt
        uv pip install -e .
    else
        echo "requirements.txt not found. Please run 'just requirements' first"
        exit 1
    fi

# Check if required dev tools are installed
check-dev-deps:
    #!/usr/bin/env sh
    if ! command -v ruff > /dev/null || ! command -v black > /dev/null; then
        echo "Development dependencies missing. Please run 'just install' first"
        exit 1
    fi

# Database commands
migrate:
    {{python}} manage.py migrate

makemigrations:
    {{python}} manage.py makemigrations

# Development server
run:
    {{python}} manage.py runserver

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
lint: check-dev-deps
    uv run ruff check . --fix

format: check-dev-deps
    uv run black .

# Django management
superuser:
    {{python}} manage.py createsuperuser

# Generate requirements
requirements:
    #!/usr/bin/env sh
    uv pip freeze > requirements.txt
    echo "Generated requirements.txt with all dependencies"

# App creation commands
app name:
    {{python}} manage.py startapp {{name}}
    @echo "Created app {{name}} with custom template"

# Environment setup
create-env:
    #!/usr/bin/env sh
    if [ ! -f .env ]; then
        cp .env.template .env
        echo "Created .env file from .env.template"
    else
        echo ".env file already exists"
    fi

# Combined commands
setup: create-env install migrate superuser

# Development workflow
dev:
    just format || true
    just lint || true
    just run
