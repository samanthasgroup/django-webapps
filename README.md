# django-webapps
Backend for the database, implemented in Django

## For developers

1. Clone this repository
2. Install [Poetry](https://github.com/python-poetry/poetry)
3. Run `poetry install` in the project directory to [install dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies).
4. Install pre-commit hooks: `pre-commit install`. They will run on files being committed. To check all code, run `pre-commit run -a`.
5. Create database migrations: `python manage.py makemigrations api`
6. Apply database migrations: `python manage.py migrate`
7. Create a superuser for admin interface: `python manage.py createsuperuser`
8. Run the server locally: `python manage.py runserver`

The main page is the admin page, as no user-facing web interface is planned yet.
