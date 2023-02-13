from django.contrib import admin

import api.models as models

for model in (
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.CoordinatorLogEventName,
    models.CoordinatorStatusName,
    models.DayOfWeek,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.GroupLogEventName,
    models.GroupStatusName,
    models.InformationSource,
    models.LanguageLevel,
    models.NativeLanguage,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.StudentLogEventName,
    models.StudentStatusName,
    models.Teacher,
    models.TeacherCategory,
    models.TeacherLogEvent,
    models.TeacherLogEventName,
    models.TeacherStatusName,
    models.TeachingLanguage,
    models.TimeSlot,
):
    admin.site.register(model)
