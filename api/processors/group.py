from api.models import Group
from api.processors.actions import GroupAbortProcessor, GroupStartProcessor


class GroupProcessor:
    """A Facade class providing access to actions with groups."""

    @staticmethod
    def start(group: Group) -> None:
        GroupStartProcessor(group=group).process()

    @staticmethod
    def abort(group: Group) -> None:
        GroupAbortProcessor(group=group).process()
