# django-webapps
Backend for the database, implemented in Django

## For developers

1. Clone this repository
2. Install [Poetry](https://github.com/python-poetry/poetry)
3. Run `poetry install` in the project directory to [install dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies).
4. Install pre-commit hooks: `pre-commit install`. They will run on files being committed. To check all code, run `pre-commit run -a`. If you want `black` to just reformat your file without asking you, run `black path-to-file`.
5. Create database migrations: `python manage.py makemigrations api`
6. Apply database migrations: `python manage.py migrate`
7. Create a superuser for admin interface: `python manage.py createsuperuser`
8. Run the server locally: `python manage.py runserver`

The main page is the admin page, as no user-facing web interface is planned yet.

### Some information about an architecture 

1. Django implements MTV (Model-Template-View) architecture pattern. This is almost MVC (Model-View-Controller) pattern, but with a few changes. Model is Model, Template is View and View is Controller (https://medium.com/shecodeafrica/understanding-the-mvc-pattern-in-django-edda05b9f43f). 
2. In order to follow SOLID principles we separate business logic and URL handlers.
3. Views are URL handlers. They parse parameters from http queries, call use case methods to execute business logic, get its results and send HTTP response. 
4. **TODO** beautiful architecture diagram  

