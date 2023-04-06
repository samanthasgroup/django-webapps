test:
	poetry run pytest

lint:
	pre-commit run --all-files

makemigrations:
	poetry run python manage.py makemigrations
