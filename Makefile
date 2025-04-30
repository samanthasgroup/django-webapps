start:
	uv run manage.py runserver

test:
	uv run pytest

lint:
	uv run pre-commit run --all-files

makemigrations:
	uv run manage.py makemigrations
	# $(MAKE) generate-erd

migrate:
	uv run manage.py migrate

recreate-first-migration:
	uv run manage.py migrate api zero && \
	$(MAKE) _recreate-first-migration-common
	$(MAKE) generate-erd

pull-and-recreate-first-migration:
	uv run manage.py migrate api zero && \
	git restore api/migrations/0001_initial.py && \
	git pull origin && \
	$(MAKE) _recreate-first-migration-common

_recreate-first-migration-common:
	uv run manage.py dumpdata auth -o auth_dump.json.gz && \
	uv run manage.py flush --no-input && \
	uv run manage.py loaddata auth_dump.json.gz && \
	mv ./api/migrations/0002_data_migration.py ./api/migrations/0002_data_migration.py.bak && \
	mv ./api/migrations/0003_fake_data.py ./api/migrations/0003_fake_data.py.bak && \
	rm -rf ./api/migrations/0001_initial.py && \
	uv run manage.py makemigrations && \
	mv ./api/migrations/0002_data_migration.py.bak ./api/migrations/0002_data_migration.py && \
	mv ./api/migrations/0003_fake_data.py.bak ./api/migrations/0003_fake_data.py && \
	uv run manage.py migrate && \
	rm auth_dump.json.gz

repopulate-data:
# This script will need to be changed if model migrations are added after data migrations.
	uv run manage.py migrate api 0001_initial && \
	uv run manage.py dumpdata auth -o auth_dump.json.gz && \
	uv run manage.py flush --no-input && \
	uv run manage.py loaddata auth_dump.json.gz && \
	uv run manage.py migrate && \
	rm auth_dump.json.gz

generate-erd:
	uv run manage.py graph_models --output erd.dot --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api && \
	dot -Tpng erd.dot -o ./api/models/erd.png && \
	rm erd.dot && \
	uv run manage.py graph_models --output erd_core.dot --verbose-names -I PersonalInfo,Coordinator,Student,Teacher,TeacherUnder18 --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api && \
	dot -Tpng erd_core.dot -o ./api/models/erd_core.png && \
	rm erd_core.dot


# Celery worker
celery:
	# uv run celery -A django_webapps worker --loglevel=info
	uv run celery -A celery_config worker --loglevel=info

# Celery beat
celery-beat:
	uv run celery -A celery_config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

celery-up:
	@echo "Starting Celery workers and beat..."
	uv run celery -A celery_config worker --loglevel=info & \
	uv run celery -A celery_config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


# Create and compile translations
trans-create:
	uv run manage.py makemessages -l ru

trans-comp:
	uv run manage.py compilemessages 

