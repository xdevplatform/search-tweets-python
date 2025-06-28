.PHONY: test tests test-unit test-integration test-coverage install clean

# Install dependencies
install:
	poetry install

# Run all tests
test:
	poetry run pytest

# Alias for test
tests: test

# Run only unit tests
test-unit:
	poetry run pytest -m unit

# Run only integration tests  
test-integration:
	poetry run pytest -m integration

# Run tests with coverage report
test-coverage:
	poetry run pytest --cov-fail-under=80

# Clean up generated files
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete