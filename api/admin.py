from django.contrib import admin

import api.models as models

for model in (
    models.AgeRange,
    models.Coordinator,
    models.CoordinatorLogEvent,
    models.DayAndTimeSlot,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogEvent,
    models.PersonalInfo,
    models.Student,
    models.StudentLogEvent,
    models.Teacher,
    models.TeacherLogEvent,
    models.TeacherUnder18,
    models.TeachingLanguage,
    models.TeachingLanguageAndLevel,
    models.TimeSlot,
):
    admin.site.register(model)
