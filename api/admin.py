from django.contrib import admin

import api.models as models

for model in (
    models.AgeRange,
    models.CommunicationLanguageMode,
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.CoordinatorLogEventRule,
    models.CoordinatorLogEventType,
    models.CoordinatorStatus,
    models.DayOfWeek,
    models.DayAndTimeSlot,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.GroupLogEventRule,
    models.GroupLogEventType,
    models.GroupStatus,
    models.LanguageLevel,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.StudentLogEventRule,
    models.StudentLogEventType,
    models.StudentStatus,
    models.Teacher,
    models.TeacherLogEvent,
    models.TeacherLogEventRule,
    models.TeacherLogEventType,
    models.TeacherStatus,
    models.TeachingLanguage,
    models.TeachingLanguageAndLevel,
    models.TimeSlot,
):
    admin.site.register(model)
