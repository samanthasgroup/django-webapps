from django.contrib import admin

from api import models

for model in (
    models.Coordinator,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.PersonalInfo,
    models.Student,
    models.Teacher,
    models.TeacherUnder18,
    models.Language,
    models.LanguageAndLevel,
    models.NonTeachingHelp,
):
    admin.site.register(model)
