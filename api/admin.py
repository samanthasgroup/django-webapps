from django.contrib import admin

import api.models as models

for model in (
    models.AgeRange,
    models.CommunicationLanguageMode,
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.CoordinatorLogEventName,
    models.CoordinatorStatus,
    models.DayOfWeek,
    models.DayAndTimeSlot,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.GroupLogEventName,
    models.GroupStatus,
    models.LanguageLevel,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.StudentLogEventName,
    models.StudentStatus,
    models.Teacher,
    models.TeacherLogEvent,
    models.TeacherLogEventName,
    models.TeacherStatus,
    models.TeachingLanguage,
    models.TeachingLanguageAndLevel,
    models.TimeSlot,
):
    admin.site.register(model)
