"""Abstract models that are shared between several modules."""
from django.db import models

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.personal_info import PersonalInfo


class Person(models.Model):
    """Abstract model for a coordinator/student/teacher. Stores their common fields and methods."""

    comment = models.TextField(blank=True)
    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_%(class)s",  # produces `.as_coordinator` etc.
    )
    # this will be overridden in each model: putting this here for mypy
    status = models.CharField(max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH)

    # This field is not just as a shortcut for log event timestamps: not all statuses have
    # corresponding LogEvent... objects.
    status_since = models.DateTimeField(verbose_name="status in place since")

    # TODO last contacted, last responded, scheduled date of next contact?

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.personal_info.full_name}. Status: {getattr(self, 'status')}"