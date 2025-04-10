from django.db import models
from django.utils.translation import gettext_lazy as _


class CommunicationLanguageMode(models.TextChoices):
    RU_ONLY = "ru", _("Russian only")
    UA_ONLY = "ua", _("Ukrainian only")
    RU_OR_UA = "ru_ua", _("Russian or Ukrainian")
    L2_ONLY = "l2_only", _("Only language being taught")
