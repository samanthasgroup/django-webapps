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

generate-erd:
	poetry run python manage.py graph_models --output erd.dot --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api && \
	dot -Tpng erd.dot -o ./api/models/erd.png && \
	rm erd.dot && \
	poetry run python manage.py graph_models --output erd_core.dot --verbose-names -I PersonalInfo,Coordinator,Student,Teacher --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api && \
	dot -Tpng erd_core.dot -o ./api/models/erd_core.png && \
	rm erd_core.dot

