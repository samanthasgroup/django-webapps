from api.models import Group
from api.processors.actions import GroupAbortProcessor, GroupCreateProcessor, GroupStartProcessor
from api.processors.actions.group.confirm_ready_to_start import GroupConfirmReadyToStartProcessor


class GroupProcessor:
    """A Facade class providing access to actions with groups."""

    @staticmethod
    def start(group: Group) -> None:
        GroupStartProcessor(group=group).process()

    @staticmethod
    def abort(group: Group) -> None:
        GroupAbortProcessor(group=group).process()

    @staticmethod
    def create(group: Group) -> None:
        GroupCreateProcessor(group=group).process()

    @staticmethod
    def confirm_ready_to_start(group: Group) -> None:
        GroupConfirmReadyToStartProcessor(group=group).process()
