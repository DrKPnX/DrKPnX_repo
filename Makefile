.PHONY: format lint test ci

format:
	black .

lint:
	flake8 .
	pylint log_analyzer.py
	mypy log_analyzer.p

test:
	pytest -v --cov=.

ci: lint test