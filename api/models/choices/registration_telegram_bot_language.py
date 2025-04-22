from django.db import models
from django.utils.translation import gettext_lazy as _


class RegistrationTelegramBotLanguage(models.TextChoices):
    EN = "en", _("English")
    RU = "ru", _("Russian")
    UA = "ua", _("Ukrainian")
