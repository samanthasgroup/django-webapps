from collections.abc import Iterable
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from api.models import Teacher
from api.processors.auxil.algorithms import GroupBuilderAlgorithm


class Command(BaseCommand):
    """
    Triggers automatic group creation.
    If teacher_ids are not specified, triggers for all available teachers.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--teacher_ids", nargs="*", type=int)

    def handle(self, *_: str, **options: Any) -> None:
        teachers: Iterable[Teacher] = []
        if options["teacher_ids"]:
            teachers = [
                Teacher.objects.filter(personal_info__id=teacher_id).get()
                for teacher_id in options["teacher_ids"]
            ]
            for teacher in teachers:
                if not GroupBuilderAlgorithm.is_teacher_available(teacher):
                    raise CommandError(f"Teacher {teacher} is not available.")
        else:
            # Get all available teachers if none specified
            teachers = GroupBuilderAlgorithm.get_available_teachers()

        for teacher in teachers:
            GroupBuilderAlgorithm.create_and_save_group(teacher.personal_info.pk)
