import logging
from collections.abc import Collection, Iterable
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from api.models import Teacher
from api.processors.services.group_builder import GroupBuilder

logger = logging.getLogger(__name__)
# TODO: remove
logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    """
    Triggers automatic group creation.
    If teacher_ids are not specified, triggers for all available teachers.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--teacher_ids", nargs="*", type=int)

    def handle(self, *_: str, **options: Any) -> None:
        teachers: Iterable[Teacher]
        custom_teacher_ids = options.get("teacher_ids")
        # Get all available teachers if none specified
        teachers = (
            self.get_teacher_ids(custom_teacher_ids) if custom_teacher_ids else GroupBuilder.get_available_teachers()
        )

        for teacher in teachers:
            logger.debug(teacher)
            GroupBuilder.create_and_save_group(teacher.pk)

    @staticmethod
    def get_teacher_ids(teacher_ids: Iterable[int]) -> Collection[Teacher]:
        teachers = []
        for teacher_id in teacher_ids:
            try:
                teacher = Teacher.objects.get(pk=teacher_id)
            except Teacher.DoesNotExist:
                raise CommandError(f"Teacher id does not exist: {teacher_id}")
            if not teacher.can_take_more_groups:
                raise CommandError(f"Teacher is not available: {teacher}")
            teachers.append(teacher)
        return teachers
