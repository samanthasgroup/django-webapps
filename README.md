# django-webapps
Backend for the database, implemented in Django

## For developers

1. Clone this repository
2. Install [Poetry](https://github.com/python-poetry/poetry) and use it to install [dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies).
3. Install pre-commit hooks: `pre-commit install`. To check all code, run `pre-commit run -a`.
4. Create database migrations: `python manage.py makemigrations api`
5. Apply migrations: `python manage.py migrate`
6. Create a superuser for admin interface: `python manage.py createsuperuser`
