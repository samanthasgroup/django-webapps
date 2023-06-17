from django.db import models

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.status import TeacherUnder18Status
from api.models.shared_abstract.teacher_common import TeacherCommon


class TeacherUnder18(TeacherCommon):
    """Model for a teacher under 18 years old that cannot teach groups."""

    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherUnder18Status.choices,
    )

    class Meta:
        indexes = [models.Index(fields=("status",), name="teacher_under_18_status_idx")]
        verbose_name_plural = "Teaching volunteers under 18 years of age"
