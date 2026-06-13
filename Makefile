.PHONY: help install install-dev test clean lint run dry-run

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the CLI
	pip install -e .

install-dev: ## Install with dev dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

lint: ## Run basic linting
	python -m py_compile src/doc_to_md_cli/*.py

run: ## Quick test run (requires examples/)
	doc-to-md-cli examples/ -o out/ --verbose

dry-run: ## Dry run on examples/
	doc-to-md-cli examples/ -o out/ --dry-run
