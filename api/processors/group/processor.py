from api.models import Group
from api.processors.base import Processor
from api.processors.group.actions.abort import AbortProcessor
from api.processors.group.actions.start import StartProcessor


class GroupProcessor(Processor):
    """A Facade class providing access to actions with groups."""

    @staticmethod
    def start(group: Group) -> None:
        StartProcessor.process(group)

    @staticmethod
    def abort(group: Group) -> None:
        AbortProcessor.process(group)
