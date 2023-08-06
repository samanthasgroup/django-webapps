# DO NOT USE IN PROD, WORK IN PROGRESS

from collections.abc import Iterable
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
from api.models.choices.status import GroupStatus, TeacherStatus
from api.models.language_and_level import LanguageAndLevel
from api.processors.auxil.log_event_creator import GroupLogEventCreator


class GroupManager:
    @dataclass
    class GroupSizeRestriction:
        min_number: int
        max_number: int

    @dataclass
    class GroupCandidate:
        language_and_level: LanguageAndLevel
        communication_language_mode: CommunicationLanguageMode
        age_range: AgeRange
        teacher: Teacher
        students: list[Student]
        monday: datetime | None = None
        tuesday: datetime | None = None
        wednesday: datetime | None = None
        thursday: datetime | None = None
        friday: datetime | None = None
        saturday: datetime | None = None
        sunday: datetime | None = None

        def is_acceptable(self) -> bool:
            # Checks group size is appropriate for age range
            restrictions = GroupManager._get_allowed_group_size(self.age_range)
            students_num = len(self.students)
            if restrictions.min_number > students_num:
                return False
            if restrictions.max_number < students_num:
                raise ValueError(
                    f"Group candidate must respect upper group boundaries, "
                    f"but {students_num} > {restrictions.max_number}"
                )
            return True

    @staticmethod
    def get_available_teachers() -> Iterable[Teacher]:
        return Teacher.objects.filter(
            status__in=(
                TeacherStatus.AWAITING_OFFER,
                TeacherStatus.TEACHING_ACCEPTING_MORE,
            )
        )

    @staticmethod
    def create_group(teacher_id: int) -> Group | None:
        for group_candidate in GroupManager._iterate_group_candidates(teacher_id):
            if group_candidate.is_acceptable():
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
                    obj=group, status=GroupStatus.PENDING, status_since=group_creation_timestamp
                )
                group.save()
                group.teachers.add(group_candidate.teacher)
                group.students.set(group_candidate.students)

                # QQ: do we update teacher/student status automatically,
                # or wait for coordinator action?
                next_teacher_status = (
                    TeacherStatus.TEACHING_ANOTHER_GROUP_OFFERED
                    if group_candidate.teacher.status == TeacherStatus.TEACHING_ACCEPTING_MORE
                    else TeacherStatus.GROUP_OFFERED
                )
                StatusSetter.set_status(
                    obj=group_candidate.teacher,
                    status=next_teacher_status,
                    status_since=group_creation_timestamp,
                )
                GroupManager._create_log_events(group)
                return group
        # No suitable groups found
        return None

    @staticmethod
    def _get_allowed_group_size(age_range: AgeRange) -> GroupSizeRestriction:
        if MAX_AGE_TEEN_GROUP < age_range.age_from <= age_range.age_to:
            return GroupManager.GroupSizeRestriction(min_number=5, max_number=10)
        if MAX_AGE_KIDS_GROUP <= age_range.age_from <= age_range.age_to <= MAX_AGE_TEEN_GROUP:
            return GroupManager.GroupSizeRestriction(min_number=2, max_number=8)
        if 0 <= age_range.age_from <= age_range.age_to <= MAX_AGE_KIDS_GROUP:
            return GroupManager.GroupSizeRestriction(min_number=2, max_number=6)
        # If age range does not fall into expected ranges, fail early
        raise ValueError(f"Group age range is inconsistent with boundaries: {age_range}")

    @staticmethod
    def _iterate_group_candidates(teacher_id: int) -> Iterable[GroupCandidate]:
        # THIS IS A STUB METHOD RETURNING DUMMY VALUES
        # TODO filter for language+level, communication language, age groups, time slots (all UTC?)
        # TODO iterate in correct priority order, yield results
        teacher = Teacher.objects.filter(personal_info__id=teacher_id).get()

        yield GroupManager.GroupCandidate(
            age_range=AgeRange(age_from=18, age_to=90),
            language_and_level=teacher.teaching_languages_and_levels.get(),
            communication_language_mode=CommunicationLanguageMode(
                teacher.personal_info.communication_language_mode
            ),
            teacher=teacher,
            students=list(range(1, 10)),  # type: ignore
            monday=timezone.now(),
            wednesday=timezone.now(),
        )

    # QQ: do we need this?
    @staticmethod
    def _create_log_events(group: Group) -> None:
        GroupLogEventCreator.create(
            group=group,
            student_log_event_type=StudentLogEventType.GROUP_OFFERED,
            teacher_log_event_type=TeacherLogEventType.GROUP_OFFERED,
            group_log_event_type=GroupLogEventType.FORMED,
        )
