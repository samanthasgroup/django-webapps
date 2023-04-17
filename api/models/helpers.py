import abc

from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


class DataMigrationMaster(abc.ABC):
    """
    Abstract class-based variation used to make data-migrations.
    See Django docs: https://docs.djangoproject.com/en/stable/topics/migrations/#data-migrations
    """

    def __init__(self, apps: StateApps, schema_editor: DatabaseSchemaEditor):
        self.apps = apps
        self.schema_editor = schema_editor
        # Adding __call__ to a class won't work because RunPython can't create an instance and then
        # run it.  So we're running main() right after instantiating, which effectively makes
        # DataMigrationMaster into a callable with instance attributes.\

    @abc.abstractmethod
    def main(self) -> None:
        """Here should be placed data migration operations."""
        pass

    @classmethod
    def run(cls, apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
        """Runs data migration operations."""
        instance = cls(apps, schema_editor)
        instance.main()
