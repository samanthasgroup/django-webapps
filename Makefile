.PHONY: help start updev down test lint makemigrations migrate recreate-first-migration \
	pull-and-recreate-first-migration _recreate-first-migration-common repopulate-data \
	generate-erd celery celery-beat celery-up trans-create trans-comp

UV := uv run
DJANGO := $(UV) manage.py
PYTEST := $(UV) pytest
PRECOMMIT := $(UV) pre-commit
COMPOSE_DEV := docker compose -f compose.dev.yml

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Dev:"
	@echo "  start              Run Django dev server"
	@echo ""
	@echo "Docker:"
	@echo "  updev              Start dev containers (compose.dev.yml)"
	@echo "  down               Stop dev containers (compose.dev.yml)"
	@echo ""
	@echo "Tests/Lint:"
	@echo "  test               Run pytest"
	@echo "  lint               Run pre-commit on all files"
	@echo ""
	@echo "Migrations/Data:"
	@echo "  makemigrations     Create migrations"
	@echo "  migrate            Apply migrations"
	@echo "  recreate-first-migration"
	@echo "  pull-and-recreate-first-migration"
	@echo "  repopulate-data"
	@echo "  generate-erd"
	@echo ""
	@echo "Celery:"
	@echo "  celery             Start worker"
	@echo "  celery-beat        Start beat scheduler"
	@echo "  celery-up          Start worker and beat (foreground)"
	@echo ""
	@echo "i18n:"
	@echo "  trans-create       Create RU translations"
	@echo "  trans-comp         Compile translations"

start:
	$(DJANGO) runserver

updev:
	$(COMPOSE_DEV) up -d

down:
	$(COMPOSE_DEV) down

test:
	$(PYTEST)

lint:
	$(PRECOMMIT) run --all-files

makemigrations:
	$(DJANGO) makemigrations
	# $(MAKE) generate-erd

migrate:
	$(DJANGO) migrate

recreate-first-migration:
	$(DJANGO) migrate api zero && \
	$(MAKE) _recreate-first-migration-common
	$(MAKE) generate-erd

pull-and-recreate-first-migration:
	$(DJANGO) migrate api zero && \
	git restore api/migrations/0001_initial.py && \
	git pull origin && \
	$(MAKE) _recreate-first-migration-common

_recreate-first-migration-common:
	$(DJANGO) dumpdata auth -o auth_dump.json.gz && \
	$(DJANGO) flush --no-input && \
	$(DJANGO) loaddata auth_dump.json.gz && \
	mv ./api/migrations/0002_data_migration.py ./api/migrations/0002_data_migration.py.bak && \
	mv ./api/migrations/0003_fake_data.py ./api/migrations/0003_fake_data.py.bak && \
	rm -rf ./api/migrations/0001_initial.py && \
	$(DJANGO) makemigrations && \
	mv ./api/migrations/0002_data_migration.py.bak ./api/migrations/0002_data_migration.py && \
	mv ./api/migrations/0003_fake_data.py.bak ./api/migrations/0003_fake_data.py && \
	$(DJANGO) migrate && \
	rm auth_dump.json.gz

repopulate-data:
# This script will need to be changed if model migrations are added after data migrations.
	$(DJANGO) migrate api 0001_initial && \
	$(DJANGO) dumpdata auth -o auth_dump.json.gz && \
	$(DJANGO) flush --no-input && \
	$(DJANGO) loaddata auth_dump.json.gz && \
	$(DJANGO) migrate && \
	rm auth_dump.json.gz

celery:
	$(UV) celery -A celery_config worker --loglevel=info

celery-beat:
	$(UV) celery -A celery_config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

celery-up:
	@echo "Starting Celery workers and beat..."
	$(UV) celery -A celery_config worker --loglevel=info & \
	$(UV) celery -A celery_config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


# Create and compile translations
trans-create:
	$(DJANGO) makemessages -l ru

trans-comp:
	$(DJANGO) compilemessages
