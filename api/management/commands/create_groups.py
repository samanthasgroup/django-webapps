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
            teachers = Teacher.objects.filter(pk__in=options["teacher_ids"])
            for teacher in teachers:
                if not teacher.can_take_more_groups:
                    raise CommandError(f"Teacher is not available: {teacher}")
        else:
            # Get all available teachers if none specified
            teachers = GroupBuilderAlgorithm.get_available_teachers()

        for teacher in teachers:
            GroupBuilderAlgorithm.create_and_save_group(teacher.pk)
