from django.contrib import admin

import api.models as models

for model in (
    models.AgeRange,
    models.CommunicationLanguageMode,
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.CoordinatorLogEventName,
    models.CoordinatorStatusName,
    models.DayOfWeek,
    models.DayAndTimeSlot,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.GroupLogEventName,
    models.GroupStatusName,
    models.LanguageLevel,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.StudentLogEventName,
    models.StudentStatusName,
    models.Teacher,
    models.TeacherLogEvent,
    models.TeacherLogEventName,
    models.TeacherStatusName,
    models.TeachingLanguage,
    models.TimeSlot,
):
    admin.site.register(model)
