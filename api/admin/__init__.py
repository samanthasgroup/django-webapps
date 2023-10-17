from django.contrib import admin

from api import models

from .coordinator import CoordinatorAdmin
from .personal_info import PersonalInfoAdmin
from .student import StudentAdmin

admin.site.register(models.Coordinator, CoordinatorAdmin)
admin.site.register(models.PersonalInfo, PersonalInfoAdmin)
admin.site.register(models.Student, StudentAdmin)


for model in (
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.EnrollmentTestResult,
    models.Group,
    models.SpeakingClub,
    models.Teacher,
    models.TeacherUnder18,
    models.Language,
    models.LanguageAndLevel,
    models.NonTeachingHelp,
    models.CoordinatorLogEvent,
):
    admin.site.register(model)
