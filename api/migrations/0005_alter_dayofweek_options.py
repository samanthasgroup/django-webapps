# Generated by Django 4.1.7 on 2023-03-05 17:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_dayofweek_index"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dayofweek",
            options={"ordering": ("index",), "verbose_name_plural": "days of the week"},
        ),
    ]
