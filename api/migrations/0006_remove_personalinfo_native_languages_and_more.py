# Generated by Django 4.1.6 on 2023-02-22 15:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0005_agerange_student_age_range"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personalinfo",
            name="native_languages",
        ),
        migrations.DeleteModel(
            name="NativeLanguage",
        ),
    ]