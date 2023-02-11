# Generated by Django 4.1.6 on 2023-02-11 11:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0007_coordinatorstatusname_groupstatusname_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="InformationSource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name_en", models.CharField(max_length=255)),
                ("name_ru", models.CharField(max_length=255)),
                ("name_ua", models.CharField(max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="person",
            name="information_source",
            field=models.ForeignKey(
                default="", on_delete=django.db.models.deletion.PROTECT, to="api.informationsource"
            ),
            preserve_default=False,
        ),
    ]
