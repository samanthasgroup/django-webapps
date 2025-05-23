from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import DEFAULT_CHAR_FIELD_MAX_LEN
from api.models.language_and_level import LanguageAndLevel
from api.models.shared_abstract.person import Person


class TeacherCommon(Person):
    """Abstract model for common properties that adult teachers and teachers under 18 share.

    Teachers under 18 cannot teach groups but can some selected activities.
    """

    can_host_speaking_club = models.BooleanField(
        verbose_name=_("Can host speaking club"), default=False
    )
    has_hosted_speaking_club = models.BooleanField(
        verbose_name=_("Has hosted speaking club"), default=False
    )
    is_validated = models.BooleanField(
        verbose_name=_("Is validated"),
        help_text=_("Has an initial validation interview been conducted with this teacher?"),
    )
    non_teaching_help_provided_comment = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN,  # prefer this to TextField for a better search
        blank=True,
        verbose_name=_("comment on additional non-teaching skills"),
        help_text=_(
            "For adult teacher: other ways in which the applicant could help the students beside "
            "listed ones. For teacher under 18: applicant's free-text comment on how they can "
            "help our students apart from hosting speaking clubs."
        ),
    )
    teaching_languages_and_levels = models.ManyToManyField(
        LanguageAndLevel, verbose_name=_("Teaching languages and levels")
    )

    class Meta:
        abstract = True
