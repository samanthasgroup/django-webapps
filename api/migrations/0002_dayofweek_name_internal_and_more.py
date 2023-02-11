# Generated by Django 4.1.6 on 2023-02-11 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="dayofweek",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text=(
                    "Internal name to use in code. This will allow to change user-facing names "
                    "easily without breaking the code."
                ),
                max_length=50,
                unique=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="informationsource",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text=(
                    "Internal name to use in code. This will allow to change user-facing names "
                    "easily without breaking the code."
                ),
                max_length=50,
                unique=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="nativelanguage",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text=(
                    "Internal name to use in code. This will allow to change user-facing names "
                    "easily without breaking the code."
                ),
                max_length=50,
                unique=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teachercategory",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text=(
                    "Internal name to use in code. This will allow to change user-facing names "
                    "easily without breaking the code."
                ),
                max_length=50,
                unique=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teachinglanguage",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text=(
                    "Internal name to use in code. This will allow to change user-facing names "
                    "easily without breaking the code."
                ),
                max_length=50,
                unique=True,
            ),
            preserve_default=False,
        ),
    ]
