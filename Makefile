test:
	poetry run pytest

lint:
    pre-commit run --all-files
