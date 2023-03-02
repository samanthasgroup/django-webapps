# Generated by Django 4.1.7 on 2023-03-02 18:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0011_teacher_additional_skills_comment_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personalinfo",
            name="comment",
        ),
        migrations.AddField(
            model_name="coordinator",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="student",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teacher",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
    ]
