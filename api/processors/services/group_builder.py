# DO NOT USE IN PROD, WORK IN PROGRESS
import functools
import itertools
import logging
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass
from datetime import time, timedelta

from django.utils import timezone

from api.models import AgeRange, Group, Student, Teacher
from api.models.auxil.constants import (
    DEFAULT_LESSON_DURATION_MIN,
    MAX_AGE_KIDS_GROUP,
    MAX_AGE_TEEN_GROUP,
    MIN_DAYS_BETWEEN_LESSONS,
)
from api.models.auxil.status_setter import StatusSetter
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.log_event_type import GroupLogEventType, StudentLogEventType, TeacherLogEventType
from api.models.choices.status import (
    GroupProjectStatus,
    StudentProjectStatus,
    StudentSituationalStatus,
    TeacherProjectStatus,
    TeacherSituationalStatus,
)
from api.models.day_and_time_slot import DayAndTimeSlot
from api.models.language_and_level import LanguageAndLevel
from api.processors.auxil.log_event_creator import GroupLogEventCreator

logger = logging.getLogger(__name__)

MAX_WAITING_TIME = timedelta(weeks=4)
LEVEL_DIFFERENCE_THRESHOLD = 2


@dataclass
class GroupSizeRestriction:
    """
    Restrictions on student group size.

    Both min and max values are inclusive:
    group size must fit into [min; max]
    """

    min: int
    max: int

    def validate_size(self, size: int) -> None:
        if size < self.min:
            raise ValueError(f"Group candidate must respect lower group boundaries, but {size} < {self.min}")
        if size > self.max:
            raise ValueError(f"Group candidate must respect upper group boundaries, but {size} > {self.max}")


@dataclass
class GroupCandidate:
    language_and_level: LanguageAndLevel
    communication_language_mode: CommunicationLanguageMode
    age_range: AgeRange
    teacher: Teacher
    students: Collection[Student]
    day_time_slots: Iterable[DayAndTimeSlot]

    def __post_init__(self) -> None:
        # Validate group size against age-related restrictions
        restrictions = GroupBuilder._get_allowed_group_size(self.age_range)
        restrictions.validate_size(len(self.students))


class GroupBuilder:
    @staticmethod
    def get_available_teachers() -> Iterator[Teacher]:
        return filter(
            lambda t: t.can_take_more_groups,
            Teacher.objects.filter(
                project_status__in=(
                    TeacherProjectStatus.NO_GROUP_YET,
                    TeacherProjectStatus.WORKING,
                ),
                situational_status="",
            ),
        )

    @staticmethod
    def create_and_save_group(teacher_id: int) -> Group | None:
        group_candidate = GroupBuilder._get_best_group_candidate(teacher_id)
        if group_candidate is None:
            # No suitable groups found
            # TODO: log something to the bot eventually?
            return None

        datetime_kwargs = GroupBuilder._get_datetime_kwargs(group_candidate.day_time_slots)
        group = Group(
            language_and_level=group_candidate.language_and_level,
            communication_language_mode=group_candidate.communication_language_mode,
            lesson_duration_in_minutes=DEFAULT_LESSON_DURATION_MIN,
            **datetime_kwargs,
        )

        group_creation_timestamp = timezone.now()
        StatusSetter.set_status(
            obj=group,
            project_status=GroupProjectStatus.PENDING,
            status_since=group_creation_timestamp,
        )
        group.teachers.add(group_candidate.teacher)
        group.students.set(group_candidate.students)

        StatusSetter.set_status(
            obj=group_candidate.teacher,
            situational_status=TeacherSituationalStatus.GROUP_OFFERED,
            status_since=group_creation_timestamp,
        )

        for student in group_candidate.students:
            StatusSetter.set_status(
                obj=student,
                situational_status=StudentSituationalStatus.GROUP_OFFERED,
                status_since=group_creation_timestamp,
            )
        GroupBuilder._create_log_events(group)
        # TODO: post to bot webhook
        return group

    @staticmethod
    def _get_allowed_group_size(age_range: AgeRange) -> GroupSizeRestriction:
        if MAX_AGE_TEEN_GROUP < age_range.age_from <= age_range.age_to:
            return GroupSizeRestriction(min=5, max=10)
        if MAX_AGE_KIDS_GROUP <= age_range.age_from <= age_range.age_to <= MAX_AGE_TEEN_GROUP:
            return GroupSizeRestriction(min=2, max=8)
        if 0 <= age_range.age_from <= age_range.age_to <= MAX_AGE_KIDS_GROUP:
            return GroupSizeRestriction(min=2, max=6)
        # If age range does not fall into expected ranges, fail early
        raise ValueError(f"Group age range is inconsistent with boundaries: {age_range}")

    @staticmethod
    def _get_best_group_candidate(teacher_id: int) -> GroupCandidate | None:
        teacher = Teacher.objects.get(pk=teacher_id)
        group_candidates: list[GroupCandidate] = []

        for language_and_level in teacher.teaching_languages_and_levels.all():
            logger.debug(language_and_level)
            for first_time_slot, second_time_slot in GroupBuilder._iterate_lesson_times(teacher):
                for age_range in teacher.student_age_ranges.all():
                    group_candidate = GroupBuilder._build_group_candidate(
                        teacher=teacher,
                        age_range=age_range,
                        language_and_level=language_and_level,
                        day_time_slots=(first_time_slot, second_time_slot),
                    )
                    if group_candidate is not None:
                        group_candidates.append(group_candidate)

        if len(group_candidates) == 0:
            return None

        group_candidates.sort(key=functools.cmp_to_key(GroupBuilder._compare_groups_priority))
        return group_candidates[0]

    @staticmethod
    def _build_group_candidate(
        teacher: Teacher,
        age_range: AgeRange,
        language_and_level: LanguageAndLevel,
        day_time_slots: Iterable[DayAndTimeSlot],
    ) -> GroupCandidate | None:
        restrictions = GroupBuilder._get_allowed_group_size(age_range)
        communication_language = CommunicationLanguageMode(teacher.personal_info.communication_language_mode)
        students = GroupBuilder._get_students(
            language_and_level=language_and_level,
            age_range=age_range,
            communication_language=communication_language,
            day_time_slots=day_time_slots,
            max_students_num=restrictions.max,
        )
        logger.debug(students)
        if len(students) < restrictions.min:
            return None

        return GroupCandidate(
            age_range=age_range,
            language_and_level=language_and_level,
            communication_language_mode=communication_language,
            teacher=teacher,
            students=students,
            day_time_slots=day_time_slots,
        )

    @staticmethod
    def _get_students(
        language_and_level: LanguageAndLevel,
        age_range: AgeRange,
        communication_language: CommunicationLanguageMode,
        day_time_slots: Iterable[DayAndTimeSlot],
        max_students_num: int,
    ) -> list[Student]:
        # TODO: handle age ranges properly (add more ranges when necessary)
        student_manager = Student.objects.filter(
            project_status=StudentProjectStatus.NO_GROUP_YET,
            teaching_languages_and_levels=language_and_level,
            personal_info__communication_language_mode=communication_language,
            age_range__age_from__gte=age_range.age_from,
            age_range__age_to__lte=age_range.age_to,
        )
        for time_slot in day_time_slots:
            student_manager = student_manager.filter(availability_slots=time_slot)

        return list(student_manager.order_by("status_since")[:max_students_num])

    @staticmethod
    def _iterate_lesson_times(teacher: Teacher) -> Iterator[tuple[DayAndTimeSlot, DayAndTimeSlot]]:
        """
        Iterate over tuples of available time slots.
        There should be at least one free day between lessons.
        """
        teacher_availability_slots = teacher.availability_slots.all()
        for first_availability, second_availability in itertools.product(teacher_availability_slots, repeat=2):
            if GroupBuilder._availability_slots_have_break(first_availability, second_availability):
                yield first_availability, second_availability

    @staticmethod
    def _availability_slots_have_break(first_availability: DayAndTimeSlot, second_availability: DayAndTimeSlot) -> bool:
        """
        Check that second availability slot is strictly after first, but not too soon after.
        """
        first_day = first_availability.day_of_week_index
        second_day = second_availability.day_of_week_index

        if first_day >= second_day:
            return False

        days_between_two_weekdays = min((second_day - first_day) % 7, (first_day - second_day) % 7)
        return days_between_two_weekdays > MIN_DAYS_BETWEEN_LESSONS

    @staticmethod
    def _get_datetime_kwargs(day_time_slots: Iterable[DayAndTimeSlot]) -> dict[str, time]:
        """
        Convert custom day and time slots to dict in format we use in data model.

        E.g.
        {
            weekday_name: datetime.time
        }
        """
        datetime_kwargs = {}
        for day_time_slot in day_time_slots:
            day_value = day_time_slot.day_of_week_index
            day_name = DayAndTimeSlot.DayOfWeek(day_value).name.lower()
            first_hour = day_time_slot.time_slot.from_utc_hour
            datetime_kwargs[day_name] = first_hour
        return datetime_kwargs

    @staticmethod
    def _create_log_events(group: Group) -> None:
        GroupLogEventCreator.create(
            group=group,
            student_log_event_type=StudentLogEventType.GROUP_OFFERED,
            teacher_log_event_type=TeacherLogEventType.GROUP_OFFERED,
            group_log_event_type=GroupLogEventType.FORMED,
        )

    @staticmethod
    def _compare_groups_priority(group1: GroupCandidate, group2: GroupCandidate) -> int:
        """
        Compare priority of two group candidates.
        Returns:
            -1 if group1 has higher priority
            0 if both candidates have equal priority
            1 if group2 has higher priority
        """
        level_difference = abs(group1.language_and_level.level.index - group2.language_and_level.level.index)
        time_threshold = timezone.now() - MAX_WAITING_TIME

        if level_difference >= LEVEL_DIFFERENCE_THRESHOLD:
            # If levels difference is 2 or more, prefer the lower level
            if group1.language_and_level.level.index < group2.language_and_level.level.index:
                return -1
            if group1.language_and_level.level.index > group2.language_and_level.level.index:
                return 1
            # if levels are equal, compare based on waiting time

        # If levels difference is 1 or less, compare based on waiting time
        # TODO: project_status_since?
        group1_waiting_students = sum(1 for student in group1.students if student.status_since >= time_threshold)
        group2_waiting_students = sum(1 for student in group2.students if student.status_since >= time_threshold)
        if group1_waiting_students > group2_waiting_students:
            return -1
        if group1_waiting_students < group2_waiting_students:
            return 1
        return 0
