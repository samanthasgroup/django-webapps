import sys
from django.db import migrations


def no_op(apps, schema_editor):
    """
    This migration previously populated fake data.
    That functionality has been moved to the management command:
    `manage.py populate_fake_data`
    This migration is now a no-op to preserve migration history.
    """
    print(
        "\nMigration 0003_fake_data: Data population logic has been moved to a management command."
    )
    print("Run 'python manage.py populate_fake_data' to generate fake data.")
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_data_migration"),
    ]
    operations = (
        [
            # This migration will do nothing if run during tests.
            # For regular migrations, it will print a message.
            migrations.RunPython(no_op, reverse_code=migrations.RunPython.noop)
        ]
        if "test" not in " ".join(sys.argv)
        else []
    )
