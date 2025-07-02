"""Module for the Role model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class Role(models.Model):
    """A role that a teacher can have in the project."""

    name = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name=_("name"),
    )
    slug = models.SlugField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name=_("slug"),
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self) -> str:
        return self.name
