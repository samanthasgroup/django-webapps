# django-webapps
Backend for the database, implemented in Django


## API Documentation
Can be found at `/api/docs/swagger` or `/api/docs/redoc` after deployment (or when running locally).

## For developers

1. Clone this repository
2. Install [Poetry](https://github.com/python-poetry/poetry)
3. Run `poetry install` in the project directory to [install dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies).
4. Activate virtual environment: `poetry shell`.
5. Install pre-commit hooks: `pre-commit install`. They will run on files being committed. To check all code, run `pre-commit run -a`. If you want `black` to just reformat your file without asking you, run `black path-to-file` or just `black .`. Same with `isort`.
6. Copy [the sample settings file](django_webapps/settings_sample.py) to `settings.py`. For local development, you don't need to make any changes to the contents of the file.
7. Create database migrations: `python manage.py makemigrations api`
8. Apply database migrations: `python manage.py migrate`
9. Collect static content: `python manage.py collectstatic`
10. Create a superuser for admin interface: `python manage.py createsuperuser`
11. Run the server locally: `python manage.py runserver`

Note that in development mode (if you don't change the settings) you will be working with an SQLite database. Since some models contain [`JSONField`](https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.JSONField)s, it is required that your SQLite installation supports JSON. To check if it does, follow the instructions [here](https://code.djangoproject.com/wiki/JSON1Extension).

The main page is the admin page, as no user-facing web interface is planned yet.

That's it for developing locally. To set up a remote server during development, see e.g. [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04).
