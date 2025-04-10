from django.db import models
from django.utils.translation import gettext_lazy as _


class NonTeachingHelpType(models.TextChoices):
    """Choices for `NonTeachingHelp` model."""

    CV_WRITE_EDIT = ("cv_write_edit", _("CV and cover letter (write or edit)"))
    CV_PROOFREAD = ("cv_proofread", _("CV and cover letter (proofread)"))
    MOCK_INTERVIEW = ("mock_interview", _("Mock interview"))
    JOB_SEARCH = ("job_search", _("Job search"))
    CAREER_STRATEGY = ("career_strategy", _("Career strategy"))
    LINKEDIN = ("linkedin", _("LinkedIn profile"))
    CAREER_SWITCH = ("career_switch", _("Career switch"))
    PORTFOLIO = ("portfolio", _("Portfolio for creative industries"))
    UNI_ABROAD = ("uni_abroad", _("Entering a university abroad"))
    TRANSLATE_DOCS = ("translate_docs", _("Translation of documents"))
