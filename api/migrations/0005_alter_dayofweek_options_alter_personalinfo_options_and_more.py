# Generated by Django 4.1.7 on 2023-03-02 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_remove_teacher_categories_delete_teachercategory"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dayofweek",
            options={"verbose_name_plural": "days of the week"},
        ),
        migrations.AlterModelOptions(
            name="personalinfo",
            options={
                "ordering": ("last_name", "first_name"),
                "verbose_name_plural": "personal info records",
            },
        ),
        migrations.AlterModelOptions(
            name="teachinglanguageandlevel",
            options={"verbose_name_plural": "Teaching languages with levels"},
        ),
        migrations.RenameField(
            model_name="coordinatorlogevent",
            old_name="coordinator_info",
            new_name="coordinator",
        ),
        migrations.RenameField(
            model_name="studentlogevent",
            old_name="student_info",
            new_name="student",
        ),
        migrations.RenameField(
            model_name="teacherlogevent",
            old_name="teacher_info",
            new_name="teacher",
        ),
        migrations.AddField(
            model_name="coordinatorlogevent",
            name="from_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_from_self",
                to="api.group",
            ),
        ),
        migrations.AddField(
            model_name="coordinatorlogevent",
            name="to_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_to_self",
                to="api.group",
            ),
        ),
        migrations.AddField(
            model_name="grouplogevent",
            name="name",
            field=models.ForeignKey(
                default="", on_delete=django.db.models.deletion.CASCADE, to="api.grouplogeventname"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="studentlogevent",
            name="from_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_from_self",
                to="api.group",
            ),
        ),
        migrations.AddField(
            model_name="studentlogevent",
            name="to_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_to_self",
                to="api.group",
            ),
        ),
        migrations.AddField(
            model_name="teacherlogevent",
            name="from_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_from_self",
                to="api.group",
            ),
        ),
        migrations.AddField(
            model_name="teacherlogevent",
            name="to_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_to_self",
                to="api.group",
            ),
        ),
    ]
