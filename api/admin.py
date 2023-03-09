from django.contrib import admin

import api.models as models

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
):
    admin.site.register(model)
