# Noir Luxe Economy Backend Makefile

.PHONY: help dev install seed-demo reset-demo test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  dev         - Start development server"
	@echo "  install     - Install dependencies"
	@echo "  seed-demo   - Seed demo data"
	@echo "  reset-demo  - Reset demo database"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean cache files"

# Development server
dev:
	@echo "Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Seed demo data
seed-demo:
	@echo "Seeding demo data..."
	curl -X POST http://127.0.0.1:8000/api/demo/seed

# Reset demo database
reset-demo:
	@echo "Resetting demo database..."
	curl -X POST http://127.0.0.1:8000/api/demo/reset

# Run tests
test:
	@echo "Running tests..."
	python -m pytest

# Clean cache files
clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
