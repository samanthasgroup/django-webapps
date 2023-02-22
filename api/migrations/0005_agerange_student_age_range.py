# Generated by Django 4.1.6 on 2023-02-22 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_remove_personalinfo_approximate_date_of_birth"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgeRange",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("age_from", models.IntegerField()),
                ("age_to", models.IntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="student",
            name="age_range",
            field=models.ForeignKey(
                default=None,
                help_text="We do not ask students for their exact age. They choose an age range when registering with us.",
                on_delete=django.db.models.deletion.PROTECT,
                to="api.agerange",
            ),
            preserve_default=False,
        ),
    ]