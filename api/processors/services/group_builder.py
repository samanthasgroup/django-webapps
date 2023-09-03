# DO NOT USE IN PROD, WORK IN PROGRESS

from collections.abc import Collection, Iterator
from dataclasses import dataclass
from datetime import datetime

from django.utils import timezone

from api.models import AgeRange, Group, Student, Teacher
from api.models.auxil.constants import (
    DEFAULT_LESSON_DURATION_MIN,
    MAX_AGE_KIDS_GROUP,
    MAX_AGE_TEEN_GROUP,
)
from api.models.auxil.status_setter import StatusSetter
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.log_event_type import (
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import (
    GroupProjectStatus,
    StudentSituationalStatus,
    TeacherProjectStatus,
    TeacherSituationalStatus,
)
from api.models.language_and_level import LanguageAndLevel
from api.processors.auxil.log_event_creator import GroupLogEventCreator


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
        if self.min > size:
            raise ValueError(
                f"Group candidate must respect upper group boundaries, but {size} > {self.max}"
            )
        if self.max < size:
            raise ValueError(
                f"Group candidate must respect upper group boundaries, but {size} > {self.max}"
            )


@dataclass
class GroupCandidate:
    language_and_level: LanguageAndLevel
    communication_language_mode: CommunicationLanguageMode
    age_range: AgeRange
    teacher: Teacher
    students: Collection[Student]
    monday: datetime | None = None
    tuesday: datetime | None = None
    wednesday: datetime | None = None
    thursday: datetime | None = None
    friday: datetime | None = None
    saturday: datetime | None = None
    sunday: datetime | None = None

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
        group_candidate = GroupBuilder._get_group_candidate(teacher_id)
        if group_candidate is None:
            # No suitable groups found
            # TODO: log something to the bot eventually?
            return None

        group = Group(
            language_and_level=group_candidate.language_and_level,
            communication_language_mode=group_candidate.communication_language_mode,
            lesson_duration_in_minutes=DEFAULT_LESSON_DURATION_MIN,
            monday=group_candidate.monday,
            tuesday=group_candidate.tuesday,
            wednesday=group_candidate.wednesday,
            thursday=group_candidate.thursday,
            friday=group_candidate.friday,
            saturday=group_candidate.saturday,
            sunday=group_candidate.sunday,
        )

        group_creation_timestamp = timezone.now()
        StatusSetter.set_status(
            obj=group,
            project_status=GroupProjectStatus.PENDING,
            status_since=group_creation_timestamp,
        )
        group.save()
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
    def _get_group_candidate(teacher_id: int) -> GroupCandidate | None:
        # THIS IS A STUB METHOD RETURNING DUMMY VALUES
        # TODO filter for language+level, communication language, age groups, time slots (all UTC?)
        # TODO iterate in correct priority order, yield results
        teacher = Teacher.objects.get(pk=teacher_id)

        return GroupCandidate(
            age_range=AgeRange(age_from=18, age_to=90),
            language_and_level=teacher.teaching_languages_and_levels.first(),  # type: ignore
            communication_language_mode=CommunicationLanguageMode(
                teacher.personal_info.communication_language_mode
            ),
            teacher=teacher,
            students=list(range(1, 10)),  # type: ignore
            monday=timezone.now(),
            wednesday=timezone.now(),
        )

    @staticmethod
    def _create_log_events(group: Group) -> None:
        GroupLogEventCreator.create(
            group=group,
            student_log_event_type=StudentLogEventType.GROUP_OFFERED,
            teacher_log_event_type=TeacherLogEventType.GROUP_OFFERED,
            group_log_event_type=GroupLogEventType.FORMED,
        )
