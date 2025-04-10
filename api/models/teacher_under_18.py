from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.status import TeacherProjectStatus, TeacherSituationalStatus
from api.models.shared_abstract.teacher_common import TeacherCommon


class TeacherUnder18(TeacherCommon):
    """Model for a teacher under 18 years old that cannot teach groups."""

    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherProjectStatus.choices,
        verbose_name=_("status in project"),
        help_text=_("status of this student with regard to project as a whole"),
    )
    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherSituationalStatus.choices,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=("project_status",), name="teacher_under_18_pr_status_idx"),
            models.Index(fields=("situational_status",), name="teacher_under_18_si_status_idx"),
        ]
        verbose_name_plural = _("Teachers under 18 years of age")
