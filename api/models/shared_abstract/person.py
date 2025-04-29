"""Abstract models that are shared between several modules."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.personal_info import PersonalInfo


class Person(models.Model):
    """Abstract model for a coordinator/student/teacher. Stores their common fields and methods."""

    comment = models.TextField(blank=True, verbose_name=_("comment"))
    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_%(class)s",
        verbose_name=_("personal info"),
    )
    # these will be overridden in each model: putting here for mypy
    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, verbose_name=_("project status")
    )

    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        blank=True,
        verbose_name=_("situational status"),
    )

    # This field is not just as a shortcut for log event timestamps: not all statuses may have
    # corresponding ...LogEvent objects.
    status_since = models.DateTimeField(
        verbose_name=_("status since"),
        help_text=_("date and time of last change of project-level or situational status"),
    )

    # TODO last contacted, last responded, scheduled date of next contact?

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return str(self.personal_info)
