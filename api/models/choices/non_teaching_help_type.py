from django.db import models


class NonTeachingHelpType(models.TextChoices):
    """Choices for `NonTeachingHelp` model."""

    CV_WRITE_EDIT = ("cv_write_edit", "CV and cover letter (write or edit)")
    CV_PROOFREAD = ("cv_proofread", "CV and cover letter (proofread)")
    MOCK_INTERVIEW = ("mock_interview", "Mock interview")
    JOB_SEARCH = ("job_search", "Job search")
    CAREER_STRATEGY = ("career_strategy", "Career strategy")
    LINKEDIN = ("linkedin", "LinkedIn profile")
    CAREER_SWITCH = ("career_switch", "Career switch")
    PORTFOLIO = ("portfolio", "Portfolio for creative industries")
    UNI_ABROAD = ("uni_abroad", "Entering a university abroad")
    TRANSLATE_DOCS = ("translate_docs", "Translation of documents")
