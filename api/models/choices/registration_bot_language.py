from django.db import models


class RegistrationBotLanguage(models.TextChoices):
    EN = "en", "English"
    RU = "ru", "Russian"
    UA = "ua", "Ukrainian"
