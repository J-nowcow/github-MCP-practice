.PHONY: help install install-dev test test-cov lint format clean docs server resources

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linters (ruff, mypy)"
	@echo "  format       - Format code (ruff, black)"
	@echo "  clean        - Clean cache and temporary files"
	@echo "  docs         - Generate documentation"
	@echo "  server       - Start MCP server"
	@echo "  resources    - Test resource handlers"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=mcp_github --cov-report=html --cov-report=term

# Code quality
lint:
	ruff check .
	mypy mcp_github/

format:
	ruff format .
	black .

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Development
docs:
	pdoc --html mcp_github --output-dir docs/api

server:
	python -m mcp_github.server

resources:
	python -c "from mcp_github.resources import get_pr_diff_resource, get_file_resource; print('Testing PR diff resource...'); result = get_pr_diff_resource('J-nowcow', 'github-MCP-practice', '1'); print(f'PR diff size: {result[\"metadata\"][\"size\"]} bytes'); print('Testing file resource...'); result = get_file_resource('J-nowcow', 'github-MCP-practice', 'README.md'); print(f'File size: {result[\"metadata\"][\"size\"]} bytes')"

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Version management
version:
	cz bump --yes

# Release
release: version
	git push --tags
	git push origin main

# Docker (if needed)
docker-build:
	docker build -t mcp-github .

docker-run:
	docker run -it --rm mcp-github

# Quick development setup
dev-setup: install-dev
	pre-commit install
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"
