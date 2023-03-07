from django.contrib import admin

import api.models as models

for model in (
    models.AgeRange,
    models.CommunicationLanguageMode,
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.CoordinatorLogEventType,
    models.CoordinatorStatus,
    models.DayAndTimeSlot,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.GroupLogEventType,
    models.GroupStatus,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.StudentLogEventType,
    models.StudentStatus,
    models.Teacher,
    models.TeacherLogEvent,
    models.TeacherLogEventType,
    models.TeacherStatus,
    models.TeachingLanguage,
    models.TeachingLanguageAndLevel,
    models.TimeSlot,
):
    admin.site.register(model)
