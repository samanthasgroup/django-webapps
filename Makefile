test:
	poetry run pytest

lint:
	pre-commit run --all-files

makemigrations:
	poetry run python manage.py makemigrations

recreate-first-migration:
	poetry run python manage.py migrate api zero && \
	poetry run python manage.py flush --no-input && \
	mv ./api/migrations/0002_data_migration.py ./api/migrations/0002_data_migration.py.bak && \
	rm -rf ./api/migrations/0001_initial.py && \
	poetry run python manage.py makemigrations && \
	mv ./api/migrations/0002_data_migration.py.bak ./api/migrations/0002_data_migration.py && \
	poetry run python manage.py migrate

