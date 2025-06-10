from django.contrib import admin
from reversion.admin import VersionAdmin

from api import models

from .coordinator import CoordinatorAdmin
from .group import GroupAdmin
from .personal_info import PersonalInfoAdmin
from .student import StudentAdmin
from .teacher import TeacherAdmin
from .user import CustomUserAdmin

admin.site.register(models.Coordinator, CoordinatorAdmin)
admin.site.register(models.Group, GroupAdmin)


for model in (
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.EnrollmentTestResult,
    models.SpeakingClub,
    models.TeacherUnder18,
    models.Language,
    models.LanguageAndLevel,
    models.NonTeachingHelp,
    models.CoordinatorLogEvent,
):
    admin.site.register(model, VersionAdmin)
