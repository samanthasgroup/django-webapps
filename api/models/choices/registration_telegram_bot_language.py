from django.db import models


class RegistrationTelegramBotLanguage(models.TextChoices):
    EN = "en", "English"
    RU = "ru", "Russian"
    UA = "ua", "Ukrainian"
