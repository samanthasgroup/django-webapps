# Generated by Django 4.1.7 on 2023-03-08 10:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_language_languageandlevel_speakingclub_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="enrollmenttestquestionoption",
            name="only_one_correct_option_per_question",
        ),
    ]
