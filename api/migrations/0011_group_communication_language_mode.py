# Generated by Django 4.1.6 on 2023-02-22 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0010_communicationlanguagemode_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="communication_language_mode",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.PROTECT,
                to="api.communicationlanguagemode",
            ),
            preserve_default=False,
        ),
    ]
