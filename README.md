![GitHub Actions](https://github.com/samanthasgroup/django-webapps/actions/workflows/main.yml/badge.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/samanthasgroup/django-webapps/master.svg)](https://results.pre-commit.ci/latest/github/samanthasgroup/django-webapps/master)

# django-webapps

Backend for the database, implemented in Django.

## API Documentation

Available at:

- `/docs/swagger`
- `/docs/redoc`

(after deployment or when running locally).

---

## For Developers

### Setup

1. Clone this repository.

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

3. Install dependencies:

    ```bash
    uv sync
    ```

4. Copy the environment file and configure it:

    ```bash
    cp .env.sample .env
    ```

5. Install pre-commit hooks:

    ```bash
    uv run pre-commit install
    ```

    Hooks will automatically run on commit.  
    `black` and `isort` will fix code formatting issues.

    To check all code manually:

    ```bash
    uv run pre-commit run -a
    ```

6. Start required services (PostgreSQL and Redis) using Docker Compose:

    ```bash
    docker-compose up -d
    ```

7. Create database migrations:

    ```bash
    uv run manage.py makemigrations api
    ```

8. Apply database migrations:

    ```bash
    uv run manage.py migrate
    ```

9. Collect static files:

    ```bash
    uv run manage.py collectstatic
    ```

10. Create a superuser for the admin interface:

    ```bash
    uv run manage.py createsuperuser
    ```

11. Run the server locally:

    ```bash
    uv run manage.py runserver
    ```

12. After registering a model with django-reversion, generate initial revisions:

    ```bash
    uv run manage.py createinitialrevisions
    ```

13. Run tests:

    ```bash
    uv run pytest
    ```

    Or:

    ```bash
    make test
    ```

---

### Notes

- By default, in development, an **SQLite** database is used.
- Some models use [`JSONField`](https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.JSONField), so your SQLite installation must support JSON.
- To check JSON support, see [this guide](https://code.djangoproject.com/wiki/JSON1Extension).

The main page is the Django admin page.  
No user-facing web interface is planned yet.

To set up a remote server for development, you can follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04).

---

### Troubleshooting pre-commit

If pre-commit hooks behave strangely, try:

```bash
pre-commit clean
pre-commit uninstall
pre-commit install
pre-commit run
