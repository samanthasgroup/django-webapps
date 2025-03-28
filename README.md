![GitHub Actions](https://github.com/samanthasgroup/django-webapps/actions/workflows/main.yml/badge.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/samanthasgroup/django-webapps/master.svg)](https://results.pre-commit.ci/latest/github/samanthasgroup/django-webapps/master)

# django-webapps

Backend for the database, implemented in Django

## API Documentation

Can be found at `/docs/swagger` or `/docs/redoc` after deployment (or when running locally).

## For developers

1. Clone this repository
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
3. Run `uv sync` in the project directory to [install dependencies](https://docs.astral.sh/uv/reference/cli/#uv-sync)
4. Copy [the sample settings file](django_webapps/settings_sample.py) to `settings.py`. For local development, you don't need to make any changes to the contents of the file.
5. Install pre-commit hooks: `uv run pre-commit install`. They will run on files being committed. `black` and `isort` will fix the issues automatically. To check all code, run `uv run pre-commit run -a`.
6. Create database migrations: `uv run manage.py makemigrations api`
7. Apply database migrations: `uv run manage.py migrate`
8. Collect static content: `uv run manage.py collectstatic`
9. Create a superuser for admin interface: `uv run manage.py createsuperuser`
10. Run the server locally: `uv run manage.py runserver`
11. Whenever you register a model with django-reversion, run `uv run manage.py createinitialrevisions`.
12. Run tests: `uv run pytest` (or `make test`)

Note that in development mode (if you don't change the settings) you will be working with an SQLite database. Since some models contain [`JSONField`](https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.JSONField)s, it is required that your SQLite installation supports JSON. To check if it does, follow the instructions [here](https://code.djangoproject.com/wiki/JSON1Extension).

The main page is the admin page, as no user-facing web interface is planned yet.

That's it for developing locally. To set up a remote server during development, see e.g. [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04).

### Side notes

If pre-commit hooks produce strange errors that definitely shouldn't be there, re-installing pre-commit could help:

```bash
pre-commit clean
pre-commit uninstall
pre-commit install
pre-commit run
```

### Licenses of 3rd-party packages

_DoubleScroll_ is dual-licensed under the MIT and GPL licenses:

* <http://www.opensource.org/licenses/mit-license.php>
* <http://www.gnu.org/licenses/gpl.html>
