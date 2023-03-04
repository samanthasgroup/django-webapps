# Generated by Django 4.1.7 on 2023-03-04 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_agerange_communicationlanguagemode_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CoordinatorLogEventRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
                (
                    "statuses_to_set",
                    models.JSONField(
                        help_text="JSON describing what object must get what status when the event is triggered"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Rules for status changes after coordinator events",
            },
        ),
        migrations.CreateModel(
            name="CoordinatorLogEventType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GroupLogEventRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
                (
                    "statuses_to_set",
                    models.JSONField(
                        help_text="JSON describing what object must get what status when the event is triggered"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Rules for status changes after group events",
            },
        ),
        migrations.CreateModel(
            name="GroupLogEventType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SpeakingClub",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("telegram_chat_url", models.URLField(blank=True, null=True)),
                (
                    "is_for_children",
                    models.BooleanField(
                        default=False, verbose_name="Is this a speaking club for children?"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StudentLogEventRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
                (
                    "statuses_to_set",
                    models.JSONField(
                        help_text="JSON describing what object must get what status when the event is triggered"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Rules for status changes after student events",
            },
        ),
        migrations.CreateModel(
            name="StudentLogEventType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeacherLogEventRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
                (
                    "statuses_to_set",
                    models.JSONField(
                        help_text="JSON describing what object must get what status when the event is triggered"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Rules for status changes after teacher events",
            },
        ),
        migrations.CreateModel(
            name="TeacherLogEventType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name_internal",
                    models.CharField(
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                        max_length=50,
                        unique=True,
                        verbose_name="internal name",
                    ),
                ),
                (
                    "name_for_user",
                    models.CharField(max_length=100, verbose_name="Readable name for coordinator"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeacherUnder18",
            fields=[
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "personal_info",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="as_%(class)s",
                        serialize=False,
                        to="api.personalinfo",
                    ),
                ),
                ("status_since", models.DateTimeField(auto_now=True)),
                (
                    "additional_skills_comment",
                    models.CharField(
                        blank=True,
                        help_text="other ways in which the applicant could help, besides teaching or helping otherteachers with materials or feedback (comment)",
                        max_length=255,
                        null=True,
                        verbose_name="Comment on additional skills besides teaching",
                    ),
                ),
                ("can_help_with_speaking_club", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name_plural": "Teaching volunteers under 18 years of age",
            },
        ),
        migrations.DeleteModel(
            name="GroupLogEventName",
        ),
        migrations.AlterModelOptions(
            name="coordinatorstatus",
            options={"verbose_name_plural": "possible coordinator statuses"},
        ),
        migrations.AlterModelOptions(
            name="dayofweek",
            options={"verbose_name_plural": "days of the week"},
        ),
        migrations.AlterModelOptions(
            name="groupstatus",
            options={"verbose_name_plural": "possible group statuses"},
        ),
        migrations.AlterModelOptions(
            name="personalinfo",
            options={
                "ordering": ("last_name", "first_name"),
                "verbose_name_plural": "personal info records",
            },
        ),
        migrations.AlterModelOptions(
            name="studentstatus",
            options={"verbose_name_plural": "possible student statuses (group studies)"},
        ),
        migrations.AlterModelOptions(
            name="teacherstatus",
            options={"verbose_name_plural": "possible teacher statuses (group studies)"},
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
            model_name="enrollmenttestresult",
            old_name="student_info",
            new_name="student",
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
        migrations.RemoveField(
            model_name="agerange",
            name="name",
        ),
        migrations.RemoveField(
            model_name="coordinatorlogevent",
            name="name",
        ),
        migrations.RemoveField(
            model_name="coordinatorstatus",
            name="in_place_since",
        ),
        migrations.RemoveField(
            model_name="coordinatorstatus",
            name="name",
        ),
        migrations.RemoveField(
            model_name="groupstatus",
            name="in_place_since",
        ),
        migrations.RemoveField(
            model_name="groupstatus",
            name="name",
        ),
        migrations.RemoveField(
            model_name="personalinfo",
            name="availability_slots",
        ),
        migrations.RemoveField(
            model_name="personalinfo",
            name="comment",
        ),
        migrations.RemoveField(
            model_name="student",
            name="status",
        ),
        migrations.RemoveField(
            model_name="studentlogevent",
            name="name",
        ),
        migrations.RemoveField(
            model_name="studentstatus",
            name="in_place_since",
        ),
        migrations.RemoveField(
            model_name="studentstatus",
            name="name",
        ),
        migrations.RemoveField(
            model_name="teacher",
            name="categories",
        ),
        migrations.RemoveField(
            model_name="teacher",
            name="status",
        ),
        migrations.RemoveField(
            model_name="teacherlogevent",
            name="name",
        ),
        migrations.RemoveField(
            model_name="teacherstatus",
            name="in_place_since",
        ),
        migrations.RemoveField(
            model_name="teacherstatus",
            name="name",
        ),
        migrations.AddField(
            model_name="coordinator",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="coordinator",
            name="mentor",
            field=models.ForeignKey(
                blank=True,
                help_text="mentor of this coordinator. One coordinator can have many interns",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interns",
                to="api.coordinator",
            ),
        ),
        migrations.AddField(
            model_name="coordinator",
            name="status_since",
            field=models.DateTimeField(auto_now=True),
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
            model_name="coordinatorstatus",
            name="name_for_user",
            field=models.CharField(
                default="", max_length=100, verbose_name="Readable name for coordinator"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="coordinatorstatus",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="group",
            name="status_since",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="groupstatus",
            name="name_for_user",
            field=models.CharField(
                default="", max_length=100, verbose_name="Readable name for coordinator"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="groupstatus",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="student",
            name="availability_slots",
            field=models.ManyToManyField(to="api.dayandtimeslot"),
        ),
        migrations.AddField(
            model_name="student",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="student",
            name="group_status",
            field=models.ForeignKey(
                default=None,
                help_text="Status of this student with regard to group studies",
                on_delete=django.db.models.deletion.PROTECT,
                to="api.studentstatus",
                verbose_name="Group studies status",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="student",
            name="smalltalk_test_result",
            field=models.JSONField(
                blank=True, help_text="JSON received from SmallTalk API", null=True
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="status_since",
            field=models.DateTimeField(auto_now=True),
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
            model_name="studentstatus",
            name="name_for_user",
            field=models.CharField(
                default="", max_length=100, verbose_name="Readable name for coordinator"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="studentstatus",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teacher",
            name="additional_skills_comment",
            field=models.CharField(
                blank=True,
                help_text="other ways in which the applicant could help, besides teaching or helping otherteachers with materials or feedback (comment)",
                max_length=255,
                null=True,
                verbose_name="Comment on additional skills besides teaching",
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="availability_slots",
            field=models.ManyToManyField(to="api.dayandtimeslot"),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_check_syllabus",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_consult_other_teachers",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_give_feedback",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_help_with_children_group",
            field=models.BooleanField(
                default=False, verbose_name="can help with children's groups"
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_help_with_cv",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_help_with_materials",
            field=models.BooleanField(
                default=False, verbose_name="can help with teaching materials"
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_help_with_speaking_club",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_invite_to_class",
            field=models.BooleanField(
                default=False, verbose_name="can invite other teachers to their class"
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="can_work_in_tandem",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teacher",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teacher",
            name="group_status",
            field=models.ForeignKey(
                default=None,
                help_text="Status of this teacher with regard to group studies.",
                on_delete=django.db.models.deletion.PROTECT,
                to="api.teacherstatus",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teacher",
            name="status_since",
            field=models.DateTimeField(auto_now=True),
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
        migrations.AddField(
            model_name="teacherstatus",
            name="name_for_user",
            field=models.CharField(
                default="", max_length=100, verbose_name="Readable name for coordinator"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teacherstatus",
            name="name_internal",
            field=models.CharField(
                default="",
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="agerange",
            name="age_from",
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="agerange",
            name="age_to",
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="communicationlanguagemode",
            name="name_en",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in English"),
        ),
        migrations.AlterField(
            model_name="communicationlanguagemode",
            name="name_internal",
            field=models.CharField(
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
        ),
        migrations.AlterField(
            model_name="communicationlanguagemode",
            name="name_ru",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in Russian"),
        ),
        migrations.AlterField(
            model_name="communicationlanguagemode",
            name="name_ua",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in Ukrainian"),
        ),
        migrations.AlterField(
            model_name="coordinator",
            name="personal_info",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="as_%(class)s",
                serialize=False,
                to="api.personalinfo",
            ),
        ),
        migrations.AlterField(
            model_name="dayofweek",
            name="name_en",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in English"),
        ),
        migrations.AlterField(
            model_name="dayofweek",
            name="name_internal",
            field=models.CharField(
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
        ),
        migrations.AlterField(
            model_name="dayofweek",
            name="name_ru",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in Russian"),
        ),
        migrations.AlterField(
            model_name="dayofweek",
            name="name_ua",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in Ukrainian"),
        ),
        migrations.AlterField(
            model_name="group",
            name="language_and_level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.teachinglanguageandlevel"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="lesson_duration",
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="languagelevel",
            name="rank",
            field=models.PositiveSmallIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name="student",
            name="personal_info",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="as_%(class)s",
                serialize=False,
                to="api.personalinfo",
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="has_prior_teaching_experience",
            field=models.BooleanField(
                default=False,
                help_text="Has the applicant already worked as a teacher before applying at Samantha Smith's Group?",
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="personal_info",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="as_%(class)s",
                serialize=False,
                to="api.personalinfo",
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="simultaneous_groups",
            field=models.PositiveSmallIntegerField(
                default=1, help_text="Number of groups the teacher can teach simultaneously"
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="weekly_frequency_per_group",
            field=models.PositiveSmallIntegerField(
                help_text="Number of times per week the teacher can have classes with each group"
            ),
        ),
        migrations.AlterField(
            model_name="teachinglanguage",
            name="name_en",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in English"),
        ),
        migrations.AlterField(
            model_name="teachinglanguage",
            name="name_internal",
            field=models.CharField(
                help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code. Internal name must not change after adding it.",
                max_length=50,
                unique=True,
                verbose_name="internal name",
            ),
        ),
        migrations.AlterField(
            model_name="teachinglanguage",
            name="name_ru",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in Russian"),
        ),
        migrations.AlterField(
            model_name="teachinglanguage",
            name="name_ua",
            field=models.CharField(max_length=255, unique=True, verbose_name="name in Ukrainian"),
        ),
        migrations.AddConstraint(
            model_name="agerange",
            constraint=models.UniqueConstraint(fields=("age_from", "age_to"), name="age_from_to"),
        ),
        migrations.AddConstraint(
            model_name="communicationlanguagemode",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="fcommunicationlanguagemode_name_internal"
            ),
        ),
        migrations.AddConstraint(
            model_name="dayandtimeslot",
            constraint=models.UniqueConstraint(
                fields=("day_of_week", "time_slot"), name="day_and_slot"
            ),
        ),
        migrations.AddConstraint(
            model_name="group",
            constraint=models.UniqueConstraint(
                fields=("telegram_chat_url",), name="telegram_chat_url"
            ),
        ),
        migrations.AddConstraint(
            model_name="personalinfo",
            constraint=models.UniqueConstraint(
                fields=("first_name", "last_name", "email"), name="full_name_and_email"
            ),
        ),
        migrations.AddConstraint(
            model_name="teachinglanguage",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="fteachinglanguage_name_internal"
            ),
        ),
        migrations.AddConstraint(
            model_name="timeslot",
            constraint=models.UniqueConstraint(
                fields=("from_utc_hour", "to_utc_hour"), name="from_to_hour"
            ),
        ),
        migrations.DeleteModel(
            name="CoordinatorLogEventName",
        ),
        migrations.DeleteModel(
            name="CoordinatorStatusName",
        ),
        migrations.DeleteModel(
            name="GroupStatusName",
        ),
        migrations.DeleteModel(
            name="StudentLogEventName",
        ),
        migrations.DeleteModel(
            name="StudentStatusName",
        ),
        migrations.DeleteModel(
            name="TeacherCategory",
        ),
        migrations.DeleteModel(
            name="TeacherLogEventName",
        ),
        migrations.DeleteModel(
            name="TeacherStatusName",
        ),
        migrations.AddConstraint(
            model_name="teacherlogeventtype",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="fteacherlogeventtype_name_internal"
            ),
        ),
        migrations.AddField(
            model_name="teacherlogeventrule",
            name="log_event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.teacherlogeventtype"
            ),
        ),
        migrations.AddConstraint(
            model_name="studentlogeventtype",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="fstudentlogeventtype_name_internal"
            ),
        ),
        migrations.AddField(
            model_name="studentlogeventrule",
            name="log_event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.studentlogeventtype"
            ),
        ),
        migrations.AddField(
            model_name="speakingclub",
            name="coordinators",
            field=models.ManyToManyField(to="api.coordinator"),
        ),
        migrations.AddField(
            model_name="speakingclub",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.teachinglanguage"
            ),
        ),
        migrations.AddField(
            model_name="speakingclub",
            name="students",
            field=models.ManyToManyField(to="api.student"),
        ),
        migrations.AddField(
            model_name="speakingclub",
            name="teachers",
            field=models.ManyToManyField(to="api.teacher"),
        ),
        migrations.AddConstraint(
            model_name="grouplogeventtype",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="fgrouplogeventtype_name_internal"
            ),
        ),
        migrations.AddField(
            model_name="grouplogeventrule",
            name="log_event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.grouplogeventtype"
            ),
        ),
        migrations.AddConstraint(
            model_name="coordinatorlogeventtype",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="fcoordinatorlogeventtype_name_internal"
            ),
        ),
        migrations.AddField(
            model_name="coordinatorlogeventrule",
            name="log_event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.coordinatorlogeventtype"
            ),
        ),
        migrations.AddField(
            model_name="coordinatorlogevent",
            name="type",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.coordinatorlogeventtype",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="grouplogevent",
            name="type",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.grouplogeventtype",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="studentlogevent",
            name="type",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.studentlogeventtype",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teacherlogevent",
            name="type",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.teacherlogeventtype",
            ),
            preserve_default=False,
        ),
    ]
