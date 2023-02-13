# Generated by Django 4.1.6 on 2023-02-13 18:14

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CoordinatorLogEventName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CoordinatorStatusName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DayAndTimeSlot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DayOfWeek",
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
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code.",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("name_en", models.CharField(max_length=255, unique=True)),
                ("name_ru", models.CharField(max_length=255, unique=True)),
                ("name_ua", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EnrollmentTest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EnrollmentTestQuestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("text", models.CharField(max_length=255, unique=True)),
                (
                    "enrollment_test",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.enrollmenttest"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EnrollmentTestQuestionOption",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("text", models.CharField(max_length=50, unique=True)),
                ("is_correct", models.BooleanField()),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.enrollmenttestquestion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_for_staff_only", models.BooleanField(default=False)),
                ("lesson_duration", models.IntegerField()),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("telegram_chat_url", models.URLField(blank=True, null=True)),
                ("monday", models.TimeField(blank=True, null=True)),
                ("tuesday", models.TimeField(blank=True, null=True)),
                ("wednesday", models.TimeField(blank=True, null=True)),
                ("thursday", models.TimeField(blank=True, null=True)),
                ("friday", models.TimeField(blank=True, null=True)),
                ("saturday", models.TimeField(blank=True, null=True)),
                ("sunday", models.TimeField(blank=True, null=True)),
                ("availability_slot", models.ManyToManyField(to="api.dayandtimeslot")),
            ],
        ),
        migrations.CreateModel(
            name="GroupLogEventName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GroupStatusName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="InformationSource",
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
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code.",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("name_en", models.CharField(max_length=255, unique=True)),
                ("name_ru", models.CharField(max_length=255, unique=True)),
                ("name_ua", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="LanguageLevel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=3, unique=True)),
                ("rank", models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="NativeLanguage",
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
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code.",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("name_en", models.CharField(max_length=255, unique=True)),
                ("name_ru", models.CharField(max_length=255, unique=True)),
                ("name_ua", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PersonalInfo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("date_and_time_added", models.DateTimeField(auto_now_add=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("tg_username", models.CharField(blank=True, max_length=100, null=True)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=50)),
                ("tz_summer_relative_to_utc", models.IntegerField()),
                ("tz_winter_relative_to_utc", models.IntegerField()),
                ("approximate_date_of_birth", models.DateField()),
                ("registration_bot_chat_id", models.IntegerField(blank=True, null=True)),
                ("chatwoot_conversation_id", models.IntegerField(blank=True, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                ("availability_slots", models.ManyToManyField(to="api.dayandtimeslot")),
                (
                    "information_source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="api.informationsource",
                        verbose_name="how did they learn about Samantha Smith's Group?",
                    ),
                ),
                ("native_languages", models.ManyToManyField(to="api.nativelanguage")),
            ],
            options={
                "ordering": ("last_name", "first_name"),
            },
        ),
        migrations.CreateModel(
            name="StudentLogEventName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StudentStatusName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeacherCategory",
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
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code.",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("name_en", models.CharField(max_length=255, unique=True)),
                ("name_ru", models.CharField(max_length=255, unique=True)),
                ("name_ua", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeacherLogEventName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeacherStatusName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeachingLanguage",
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
                        help_text="Internal name to use in code. This will allow to change user-facing names easily without breaking the code.",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("name_en", models.CharField(max_length=255, unique=True)),
                ("name_ru", models.CharField(max_length=255, unique=True)),
                ("name_ua", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TimeSlot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("from_utc_hour", models.TimeField()),
                ("to_utc_hour", models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Coordinator",
            fields=[
                (
                    "personal_info",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="as_coordinator",
                        serialize=False,
                        to="api.personalinfo",
                    ),
                ),
                (
                    "is_admin",
                    models.BooleanField(
                        default=False,
                        help_text="This field has nothing to do with accessing Django admin site. It marks coordinators that have special rights over ordinary coordinators.",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "personal_info",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="as_student",
                        serialize=False,
                        to="api.personalinfo",
                    ),
                ),
                ("requires_communication_in_ukrainian", models.BooleanField(default=False)),
                (
                    "is_member_of_speaking_club",
                    models.BooleanField(
                        default=False,
                        help_text="Is the student a member of a speaking club at the moment?",
                        verbose_name="Speaking club status",
                    ),
                ),
                (
                    "requires_help_with_CV",
                    models.BooleanField(
                        default=False,
                        help_text="Does the student need help with CV at the moment?",
                        verbose_name="CV help status",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                (
                    "personal_info",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="as_teacher",
                        serialize=False,
                        to="api.personalinfo",
                    ),
                ),
                ("categories", models.ManyToManyField(to="api.teachercategory")),
            ],
        ),
        migrations.CreateModel(
            name="TeachingLanguageAndLevel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.teachinglanguage"
                    ),
                ),
                (
                    "level",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.languagelevel"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TeacherStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("in_place_since", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.teacherstatusname"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StudentStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("in_place_since", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.studentstatusname"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GroupStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("in_place_since", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.groupstatusname"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GroupLogEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                (
                    "group",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.group"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="group",
            name="language_and_level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.teachinglanguageandlevel"
            ),
        ),
        migrations.AddField(
            model_name="group",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.groupstatus"
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttest",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.teachinglanguage"
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttest",
            name="levels",
            field=models.ManyToManyField(to="api.languagelevel"),
        ),
        migrations.AddField(
            model_name="dayandtimeslot",
            name="day_of_week",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.dayofweek"
            ),
        ),
        migrations.AddField(
            model_name="dayandtimeslot",
            name="time_slot",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.timeslot"
            ),
        ),
        migrations.CreateModel(
            name="CoordinatorStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("in_place_since", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.coordinatorstatusname"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeacherLogEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.teacherlogeventname"
                    ),
                ),
                (
                    "teacher_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="log",
                        to="api.teacher",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="teacher",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.teacherstatus"
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="teaching_languages_and_levels",
            field=models.ManyToManyField(to="api.teachinglanguageandlevel"),
        ),
        migrations.CreateModel(
            name="StudentLogEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.studentlogeventname"
                    ),
                ),
                (
                    "student_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="log",
                        to="api.student",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="student",
            name="status",
            field=models.ForeignKey(
                help_text="Status of a student with regard to group studies",
                on_delete=django.db.models.deletion.PROTECT,
                to="api.studentstatus",
                verbose_name="Group studies status",
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="teaching_languages_and_levels",
            field=models.ManyToManyField(to="api.teachinglanguageandlevel"),
        ),
        migrations.AddField(
            model_name="group",
            name="coordinators",
            field=models.ManyToManyField(to="api.coordinator"),
        ),
        migrations.AddField(
            model_name="group",
            name="students",
            field=models.ManyToManyField(to="api.student"),
        ),
        migrations.AddField(
            model_name="group",
            name="teachers",
            field=models.ManyToManyField(to="api.teacher"),
        ),
        migrations.CreateModel(
            name="EnrollmentTestResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("answers", models.ManyToManyField(to="api.enrollmenttestquestionoption")),
                (
                    "student_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.student"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CoordinatorLogEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.coordinatorlogeventname",
                    ),
                ),
                (
                    "coordinator_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="log",
                        to="api.coordinator",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="coordinator",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.coordinatorstatus"
            ),
        ),
    ]
