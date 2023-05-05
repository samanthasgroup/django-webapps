test:
	poetry run pytest

lint:
	pre-commit run --all-files

makemigrations:
	poetry run python manage.py makemigrations
	$(MAKE) generate-erd

migrate:
	poetry run python manage.py migrate

recreate-first-migration:
	poetry run python manage.py migrate api zero && \
	poetry run python manage.py dumpdata auth -o auth_dump.json.gz && \
	poetry run python manage.py flush --no-input && \
	poetry run python manage.py loaddata auth_dump.json.gz && \
	mv ./api/migrations/0002_data_migration.py ./api/migrations/0002_data_migration.py.bak && \
	mv ./api/migrations/0003_fake_data.py ./api/migrations/0003_fake_data.py.bak && \
	rm -rf ./api/migrations/0001_initial.py && \
	poetry run python manage.py makemigrations && \
	mv ./api/migrations/0002_data_migration.py.bak ./api/migrations/0002_data_migration.py && \
	mv ./api/migrations/0003_fake_data.py.bak ./api/migrations/0003_fake_data.py && \
	poetry run python manage.py migrate && \
	rm auth_dump.json.gz
	$(MAKE) generate-erd

repopulate-data:
# This script will need to be changed if model migrations are added after data migrations.
	poetry run python manage.py migrate api 0001_initial && \
	poetry run python manage.py dumpdata auth -o auth_dump.json.gz && \
	poetry run python manage.py flush --no-input && \
	poetry run python manage.py loaddata auth_dump.json.gz && \
	poetry run python manage.py migrate && \
	rm auth_dump.json.gz

generate-erd:
	poetry run python manage.py graph_models --output erd.dot --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api && \
	dot -Tpng erd.dot -o ./api/models/erd.png && \
	rm erd.dot && \
	poetry run python manage.py graph_models --output erd_core.dot --verbose-names -I PersonalInfo,Coordinator,Student,Teacher,TeacherUnder18 --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api && \
	dot -Tpng erd_core.dot -o ./api/models/erd_core.png && \
	rm erd_core.dot

