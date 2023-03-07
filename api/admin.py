from django.contrib import admin

import api.models as models

for model in (
    models.AgeRange,
    models.CommunicationLanguageMode,
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.CoordinatorLogEventType,
    models.DayAndTimeSlot,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.GroupLogEventType,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.StudentLogEventType,
    models.Teacher,
    models.TeacherLogEvent,
    models.TeacherLogEventType,
    models.TeacherUnder18,
    models.TeachingLanguage,
    models.TeachingLanguageAndLevel,
    models.TimeSlot,
):
    admin.site.register(model)
