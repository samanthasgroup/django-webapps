from django.contrib import admin

import api.models as models

for model in (
    models.Coordinator,
    models.CoordinatorLogItemName,
    models.CoordinatorStatusName,
    models.DayOfWeek,
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.Group,
    models.GroupLogItemName,
    models.GroupStatusName,
    models.InformationSource,
    models.LanguageLevel,
    models.NativeLanguage,
    models.PersonalInfo,
    models.Student,
    models.StudentLogItemName,
    models.StudentStatusName,
    models.Teacher,
    models.TeacherCategory,
    models.TeacherLogItemName,
    models.TeacherStatusName,
    models.TeachingLanguage,
    models.TimeSlot,
):
    admin.site.register(model)
