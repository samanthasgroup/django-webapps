import uuid
from collections.abc import Iterable
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field import modelfields

from api.models.choices.registration_telegram_bot_language import RegistrationTelegramBotLanguage
from api.models.shared_abstract.group_or_person import GroupOrPerson
from api.utils import capitalize_each_word


# One person can perform several roles.  Therefore, the logic proposed is as follows: first,
# a PersonalInfo is created, then e.g. a Coordinator is created, linking to that PersonalInfo.
# Then, if the same person assumes another role, e.g. a Teacher is created, linking to the
# existing PersonalInfo.
class PersonalInfo(GroupOrPerson):
    """Model for storing personal information.

    This model does not depend on a person's role (coordinators, students and teachers).
    """

    # One ID will identify a person with any role (student, teacher, coordinator),
    # even if one person combines several roles.  The autoincrement simple numeric ID can be used
    # for internal communication ("John 132"), while uuid can be used e.g. for hyperlinks
    # to prevent IDOR
    uuid = models.UUIDField(
        verbose_name=_("autogenerated unique identifier"), default=uuid.uuid4, editable=False
    )
    # Automatically save date and time when the Person was created.
    date_and_time_added = models.DateTimeField(
        verbose_name=_("Date and time added"), auto_now_add=True
    )
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    # Telegram's limit is 32, but this might change
    # These are none for coordinator, but can be present for student/teacher, so keeping them here.
    telegram_username = models.CharField(
        verbose_name=_("Telegram username"), max_length=100, blank=True
    )
    email = models.EmailField(verbose_name=_("Email"))
    phone = modelfields.PhoneNumberField(verbose_name=_("Phone number"), null=True, blank=True)
    utc_timedelta = models.DurationField(
        verbose_name=_("Difference between person's local time zone and UTC"),
        default=timedelta(hours=0),
    )
    information_source = models.TextField(
        verbose_name=_("Source of information about SSG"),
        help_text=_("How did they learn about Samantha Smith's Group?"),
    )
    # Also, there is a possibility that coordinators will register with registration bot someday.
    registration_telegram_bot_chat_id = models.BigIntegerField(
        verbose_name=_("Registration Telegram bot chat ID"), null=True, blank=True
    )
    registration_telegram_bot_language = models.CharField(
        verbose_name=_("Preferred bot language"),
        max_length=2,
        choices=RegistrationTelegramBotLanguage.choices,
        help_text=_(
            "Language in which the person wishes to communicate with the bot "
            "(is chosen by the person at first contact)"
        ),
    )
    chatwoot_conversation_id = models.PositiveIntegerField(
        verbose_name=_("Chatwoot conversation ID"), null=True, blank=True
    )

    class Meta:
        # there may be no phone or tg username, but matching name and email is good enough reason
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "email"], name="full_name_and_email"
            )
        ]
        indexes = [
            models.Index(fields=("last_name", "first_name", "email"), name="name_email_idx")
        ]
        ordering = ("last_name", "first_name")
        verbose_name_plural = _("Personal info records")

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        self.first_name = capitalize_each_word(self.first_name)
        self.last_name = capitalize_each_word(self.last_name)
        self.email = self.email.lower()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def __str__(self) -> str:
        return f"{self.pk} {self.full_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
