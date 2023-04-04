from django.db import models


class CommunicationLanguageMode(models.TextChoices):
    RU_ONLY = "ru", "Russian only"
    UA_ONLY = "ua", "Ukrainian only"
    RU_OR_UA = "ru_ua", "Russian or Ukrainian"
    L2_ONLY = "l2_only", "Only language being taught"
