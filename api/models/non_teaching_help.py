from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import DEFAULT_CHAR_FIELD_MAX_LEN
from api.models.choices.non_teaching_help_type import NonTeachingHelpType


class NonTeachingHelp(models.Model):
    """Model for ways of helping students other than teaching them foreign languages.

    Both Student and Teacher can have connections to this model, meaning that a teacher can
    provide this kind of help, while a student requires this kind of help.
    """

    id = models.CharField(
        max_length=20,
        primary_key=True,
        choices=NonTeachingHelpType.choices,
        verbose_name=_("help type id"),
    )

    name = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN, unique=True, verbose_name=_("name")
    )

    class Meta:
        verbose_name = _("non-teaching help")
        verbose_name_plural = _("non-teaching helps")

    def __str__(self) -> str:
        choices_dict = dict(NonTeachingHelpType.choices)
        return str(choices_dict.get(self.id, self.id))
