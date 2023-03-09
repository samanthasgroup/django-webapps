# Generated by Django 4.1.7 on 2023-03-09 17:03

import datetime
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

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
                ("age_from", models.PositiveSmallIntegerField()),
                (
                    "age_to",
                    models.PositiveSmallIntegerField(
                        verbose_name="End of age range (NOT inclusive!)"
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("student", "for students to select their age"),
                            ("teacher", "for teacher to select desired ages of students"),
                            ("matching", "for matching algorithm"),
                        ],
                        help_text="who/what is this range designed for",
                        max_length=15,
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
                    "type",
                    models.CharField(
                        choices=[
                            ("joined", "Joined the team"),
                            ("onboard", "Started onboarding"),
                            ("onboard_end", "Finished onboarding"),
                            ("took_group", "Took a group"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
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
                (
                    "day_of_week_index",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ],
                        verbose_name="day of the week",
                    ),
                ),
            ],
            options={
                "ordering": ("day_of_week_index", "time_slot__from_utc_hour"),
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
                ("text", models.CharField(max_length=255)),
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
                ("text", models.CharField(max_length=50)),
                ("is_correct", models.BooleanField()),
            ],
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
                (
                    "communication_language_mode",
                    models.CharField(
                        choices=[
                            ("ru", "Russian only"),
                            ("ua", "Ukrainian only"),
                            ("ru_ua", "Russian or Ukrainian"),
                            ("l2_only", "Only language being taught"),
                        ],
                        max_length=15,
                        verbose_name="Language(s) the students and teachers can speak in class",
                    ),
                ),
                ("telegram_chat_url", models.URLField(blank=True, null=True)),
                ("is_for_staff_only", models.BooleanField(default=False)),
                ("lesson_duration_in_minutes", models.PositiveSmallIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("study", "Studying"),
                            ("finish", "Finished"),
                        ],
                        max_length=15,
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("monday", models.TimeField(blank=True, null=True)),
                ("tuesday", models.TimeField(blank=True, null=True)),
                ("wednesday", models.TimeField(blank=True, null=True)),
                ("thursday", models.TimeField(blank=True, null=True)),
                ("friday", models.TimeField(blank=True, null=True)),
                ("saturday", models.TimeField(blank=True, null=True)),
                ("sunday", models.TimeField(blank=True, null=True)),
            ],
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
                    "type",
                    models.CharField(
                        choices=[
                            ("formed", "Formed"),
                            ("confirmed", "Confirmed"),
                            ("started", "Started classes"),
                            ("finished", "Finished classes"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Language",
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
            name="LanguageAndLevel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Languages with levels",
            },
        ),
        migrations.CreateModel(
            name="LanguageLevel",
            fields=[
                ("id", models.CharField(max_length=2, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="PersonalInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "communication_language_mode",
                    models.CharField(
                        choices=[
                            ("ru", "Russian only"),
                            ("ua", "Ukrainian only"),
                            ("ru_ua", "Russian or Ukrainian"),
                            ("l2_only", "Only language being taught"),
                        ],
                        max_length=15,
                        verbose_name="Language(s) the students and teachers can speak in class",
                    ),
                ),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("date_and_time_added", models.DateTimeField(auto_now_add=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("tg_username", models.CharField(blank=True, max_length=100, null=True)),
                ("email", models.EmailField(max_length=254)),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("utc_timedelta", models.DurationField(default=datetime.timedelta(0))),
                (
                    "information_source",
                    models.TextField(
                        help_text="how did they learn about Samantha Smith's Group?",
                        verbose_name="source of info about SSG",
                    ),
                ),
                ("registration_bot_chat_id", models.IntegerField(blank=True, null=True)),
                ("chatwoot_conversation_id", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "personal info records",
                "ordering": ("last_name", "first_name"),
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
                (
                    "communication_language_mode",
                    models.CharField(
                        choices=[
                            ("ru", "Russian only"),
                            ("ua", "Ukrainian only"),
                            ("ru_ua", "Russian or Ukrainian"),
                            ("l2_only", "Only language being taught"),
                        ],
                        max_length=15,
                        verbose_name="Language(s) the students and teachers can speak in class",
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
                    "type",
                    models.CharField(
                        choices=[
                            ("register", "Joined the team"),
                            ("start", "Started studying in a group"),
                            ("req_transf", "Requested transfer"),
                            ("transferred", "Transferred"),
                            ("missed_class", "Missed a class"),
                            ("finish_group", "Finished studying in a group"),
                            ("no_reply", "Not replying"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
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
                    "type",
                    models.CharField(
                        choices=[
                            ("register", "Joined the team"),
                            ("start", "Started studying in a group"),
                            ("finish_group", "Finished studying in a group"),
                            ("no_reply", "Not replying"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
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
                (
                    "is_admin",
                    models.BooleanField(
                        default=False,
                        help_text="This field has nothing to do with accessing Django admin site. It marks coordinators that have special rights over ordinary coordinators.",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("onboarding", "In onboarding"),
                            ("working", "Working with a group"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Student",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting for a group"),
                            ("study", "Studying in a group"),
                            ("transfer", "Needs transfer to another group"),
                        ],
                        help_text="status of this student with regard to group studies",
                        max_length=15,
                        verbose_name="group studies status",
                    ),
                ),
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
                (
                    "smalltalk_test_result",
                    models.JSONField(
                        blank=True, help_text="JSON received from SmallTalk API", null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Teacher",
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
                (
                    "additional_skills_comment",
                    models.CharField(
                        blank=True,
                        help_text="other ways in which the applicant could help, besides teaching or helping otherteachers with materials or feedback (comment)",
                        max_length=255,
                        null=True,
                        verbose_name="comment on additional skills besides teaching",
                    ),
                ),
                ("can_help_with_speaking_club", models.BooleanField(default=False)),
                ("can_help_with_cv", models.BooleanField(default=False)),
                ("can_check_syllabus", models.BooleanField(default=False)),
                ("can_consult_other_teachers", models.BooleanField(default=False)),
                ("can_give_feedback", models.BooleanField(default=False)),
                (
                    "can_help_with_children_group",
                    models.BooleanField(
                        default=False, verbose_name="can help with children's groups"
                    ),
                ),
                (
                    "can_help_with_materials",
                    models.BooleanField(
                        default=False, verbose_name="can help with teaching materials"
                    ),
                ),
                (
                    "can_invite_to_class",
                    models.BooleanField(
                        default=False, verbose_name="can invite other teachers to their class"
                    ),
                ),
                ("can_work_in_tandem", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting for a group"),
                            ("teaching", "Teaching a group"),
                            ("transfer", "Needs transfer to another group"),
                        ],
                        help_text="status of this teacher with regard to group studies",
                        max_length=15,
                        verbose_name="group studies status",
                    ),
                ),
                (
                    "has_prior_teaching_experience",
                    models.BooleanField(
                        default=False,
                        help_text="has the applicant already worked as a teacher before applying at Samantha Smith's Group?",
                    ),
                ),
                (
                    "simultaneous_groups",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text="number of groups the teacher can teach simultaneously",
                    ),
                ),
                (
                    "weekly_frequency_per_group",
                    models.PositiveSmallIntegerField(
                        help_text="number of times per week the teacher can have classes with each group"
                    ),
                ),
            ],
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
                (
                    "additional_skills_comment",
                    models.CharField(
                        blank=True,
                        help_text="other ways in which the applicant could help, besides teaching or helping otherteachers with materials or feedback (comment)",
                        max_length=255,
                        null=True,
                        verbose_name="comment on additional skills besides teaching",
                    ),
                ),
                ("can_help_with_speaking_club", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting for a group"),
                            ("speak_club", "Teaching in a speaking club"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Teaching volunteers under 18 years of age",
            },
        ),
        migrations.AddConstraint(
            model_name="timeslot",
            constraint=models.UniqueConstraint(
                fields=("from_utc_hour", "to_utc_hour"), name="from_to_hour"
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
            model_name="speakingclub",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.language"
            ),
        ),
        migrations.AddIndex(
            model_name="personalinfo",
            index=models.Index(fields=["last_name", "first_name", "email"], name="name_email_idx"),
        ),
        migrations.AddConstraint(
            model_name="personalinfo",
            constraint=models.UniqueConstraint(
                fields=("first_name", "last_name", "email"), name="full_name_and_email"
            ),
        ),
        migrations.AddField(
            model_name="languageandlevel",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.language"
            ),
        ),
        migrations.AddField(
            model_name="languageandlevel",
            name="level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.languagelevel"
            ),
        ),
        migrations.AddConstraint(
            model_name="language",
            constraint=models.UniqueConstraint(
                fields=("name_internal",), name="flanguage_name_internal"
            ),
        ),
        migrations.AddField(
            model_name="grouplogevent",
            name="group",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.group"),
        ),
        migrations.AddField(
            model_name="group",
            name="availability_slot",
            field=models.ManyToManyField(to="api.dayandtimeslot"),
        ),
        migrations.AddField(
            model_name="group",
            name="language_and_level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.languageandlevel"
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttestresult",
            name="answers",
            field=models.ManyToManyField(to="api.enrollmenttestquestionoption"),
        ),
        migrations.AddField(
            model_name="enrollmenttestquestionoption",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.enrollmenttestquestion"
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttestquestion",
            name="enrollment_test",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.enrollmenttest"
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttest",
            name="age_ranges",
            field=models.ManyToManyField(
                blank=True,
                help_text="age ranges for which this test was designed. Leave blank for the test to be shown to all ages.",
                to="api.agerange",
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttest",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.language"
            ),
        ),
        migrations.AddField(
            model_name="enrollmenttest",
            name="levels",
            field=models.ManyToManyField(
                blank=True,
                help_text="level(s) of the language this test was designed for. Leave blank for the test to be shown for all levels.",
                to="api.languagelevel",
            ),
        ),
        migrations.AddField(
            model_name="dayandtimeslot",
            name="time_slot",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.timeslot"
            ),
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
        migrations.AddConstraint(
            model_name="agerange",
            constraint=models.UniqueConstraint(
                fields=("age_from", "age_to", "type"), name="unique_age_and_type"
            ),
        ),
        migrations.AddIndex(
            model_name="teacherunder18",
            index=models.Index(fields=["status"], name="teacher_under_18_status_idx"),
        ),
        migrations.AddField(
            model_name="teacherlogevent",
            name="teacher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="log", to="api.teacher"
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="availability_slots",
            field=models.ManyToManyField(to="api.dayandtimeslot"),
        ),
        migrations.AddField(
            model_name="teacher",
            name="student_age_ranges",
            field=models.ManyToManyField(
                help_text="age ranges of students that the teacher is willing to teach. The 'from's and 'to's of these ranges are wider than those the students choose for themselves.",
                to="api.agerange",
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="teaching_languages_and_levels",
            field=models.ManyToManyField(to="api.languageandlevel"),
        ),
        migrations.AddField(
            model_name="studentlogevent",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="log", to="api.student"
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="age_range",
            field=models.ForeignKey(
                help_text="We do not ask students for their exact age. They choose an age range when registering with us.",
                on_delete=django.db.models.deletion.PROTECT,
                to="api.agerange",
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="availability_slots",
            field=models.ManyToManyField(to="api.dayandtimeslot"),
        ),
        migrations.AddField(
            model_name="student",
            name="teaching_languages_and_levels",
            field=models.ManyToManyField(to="api.languageandlevel"),
        ),
        migrations.AddField(
            model_name="speakingclub",
            name="coordinators",
            field=models.ManyToManyField(to="api.coordinator"),
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
        migrations.AddField(
            model_name="speakingclub",
            name="teachers_under_18",
            field=models.ManyToManyField(to="api.teacherunder18"),
        ),
        migrations.AddIndex(
            model_name="grouplogevent",
            index=models.Index(fields=["group_id"], name="group_id_idx"),
        ),
        migrations.AddIndex(
            model_name="grouplogevent",
            index=models.Index(fields=["type"], name="group_log_event_type_idx"),
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
        migrations.AddField(
            model_name="enrollmenttestresult",
            name="student",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.student"),
        ),
        migrations.AddConstraint(
            model_name="enrollmenttestquestionoption",
            constraint=models.UniqueConstraint(
                fields=("question_id", "text"), name="option_unique_per_question"
            ),
        ),
        migrations.AddConstraint(
            model_name="enrollmenttestquestion",
            constraint=models.UniqueConstraint(
                fields=("enrollment_test_id", "text"), name="option_unique_per_test"
            ),
        ),
        migrations.AddConstraint(
            model_name="dayandtimeslot",
            constraint=models.UniqueConstraint(
                fields=("day_of_week_index", "time_slot"), name="unique_day_and_slot"
            ),
        ),
        migrations.AddField(
            model_name="coordinatorlogevent",
            name="coordinator",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="log",
                to="api.coordinator",
            ),
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
        migrations.AddIndex(
            model_name="teacherlogevent",
            index=models.Index(fields=["teacher_id"], name="teacher_id_idx"),
        ),
        migrations.AddIndex(
            model_name="teacherlogevent",
            index=models.Index(fields=["type"], name="teacher_log_event_type_idx"),
        ),
        migrations.AddIndex(
            model_name="teacher",
            index=models.Index(fields=["status"], name="teacher_status_idx"),
        ),
        migrations.AddIndex(
            model_name="studentlogevent",
            index=models.Index(fields=["student_id"], name="student_id_idx"),
        ),
        migrations.AddIndex(
            model_name="studentlogevent",
            index=models.Index(fields=["type"], name="student_log_event_type_idx"),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(fields=["status"], name="student_status_idx"),
        ),
        migrations.AddIndex(
            model_name="group",
            index=models.Index(fields=["language_and_level"], name="group_language_level_idx"),
        ),
        migrations.AddIndex(
            model_name="group",
            index=models.Index(fields=["status"], name="group_status_idx"),
        ),
        migrations.AddIndex(
            model_name="group",
            index=models.Index(fields=["start_date"], name="group_start_date_idx"),
        ),
        migrations.AddConstraint(
            model_name="group",
            constraint=models.UniqueConstraint(
                fields=("telegram_chat_url",), name="telegram_chat_url"
            ),
        ),
        migrations.AddConstraint(
            model_name="group",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("monday__isnull", False),
                    ("tuesday__isnull", False),
                    ("wednesday__isnull", False),
                    ("thursday__isnull", False),
                    ("friday__isnull", False),
                    ("saturday__isnull", False),
                    ("sunday__isnull", False),
                    _connector="OR",
                ),
                name="at_least_one_day_time_slot_must_be_selected",
            ),
        ),
        migrations.AddIndex(
            model_name="coordinatorlogevent",
            index=models.Index(fields=["coordinator_id"], name="coordinator_id_idx"),
        ),
        migrations.AddIndex(
            model_name="coordinatorlogevent",
            index=models.Index(fields=["type"], name="coordinator_log_event_type_idx"),
        ),
        migrations.AddIndex(
            model_name="coordinator",
            index=models.Index(fields=["status"], name="coordinator_status_idx"),
        ),
    ]
