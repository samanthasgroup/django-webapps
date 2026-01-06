![GitHub Actions](https://github.com/samanthasgroup/django-webapps/actions/workflows/main.yml/badge.svg) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/samanthasgroup/django-webapps/master.svg)](https://results.pre-commit.ci/latest/github/samanthasgroup/django-webapps/master)

# django-webapps

Backend for the database, implemented in Django.

## Contents

- [API Documentation](#api-documentation)
- [Getting Started](#getting-started)
- [Full Setup](#full-setup)
- [Common Commands](#common-commands)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)

## API Documentation

Available after deployment or when running locally:

- `/docs/swagger`
- `/docs/redoc`

## Getting Started

Quick setup to get the app running locally:

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Install dependencies:

    ```bash
    uv sync
    ```

3. Create local environment config:

    ```bash
    cp .env.sample .env
    ```

4. Start PostgreSQL and Redis:

    ```bash
    docker compose -f compose.dev.yml up -d
    ```

    Or:

    ```bash
    make updev
    ```

5. Apply migrations:

    ```bash
    uv run manage.py migrate
    ```

6. Run the server:

    ```bash
    uv run manage.py runserver
    ```

    Or:

    ```bash
    make start
    ```

## Full Setup

Recommended for active development:

1. Install dependencies:

    ```bash
    uv sync
    ```

2. Copy the environment file and configure it:

    ```bash
    cp .env.sample .env
    ```

3. Install pre-commit hooks:

    ```bash
    uv run pre-commit install
    ```

    Hooks will automatically run on commit.  
    `black` and `isort` will fix code formatting issues.

    To check all code manually:

    ```bash
    uv run pre-commit run -a
    ```

4. Start required services (PostgreSQL and Redis) using Docker Compose:

    ```bash
    docker compose -f compose.dev.yml up -d
    ```

    Or:

    ```bash
    make updev
    ```

5. Create database migrations:

    ```bash
    uv run manage.py makemigrations api
    ```

6. Apply database migrations:

    ```bash
    uv run manage.py migrate
    ```

7. Collect static files:

    ```bash
    uv run manage.py collectstatic
    ```

8. Create a superuser for the admin interface:

    ```bash
    uv run manage.py createsuperuser
    ```

9. Run the server locally:

    ```bash
    uv run manage.py runserver
    ```

10. After registering a model with django-reversion, generate initial revisions:

    ```bash
    uv run manage.py createinitialrevisions
    ```

11. Run tests:

    ```bash
    uv run pytest
    ```

    Or:

    ```bash
    make test
    ```

## Common Commands

| Task | Command |
| --- | --- |
| Lint | `make lint` |
| Run tests | `make test` |
| Run server | `make start` |
| Create migrations (api) | `uv run manage.py makemigrations api` |
| Start Celery worker | `make celery` |
| Start Celery beat | `make celery-beat` |

## Notes

The main page is the Django admin page.  
No user-facing web interface is planned yet.

To set up a remote server for development, you can follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04).

## Troubleshooting

### pre-commit

If pre-commit hooks behave strangely, try:

```bash
pre-commit clean
pre-commit uninstall
pre-commit install
pre-commit run
