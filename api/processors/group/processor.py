from api.models import Group
from api.processors.base import Processor
from api.processors.group.actions.abort import AbortProcessor
from api.processors.group.actions.start import StartProcessor


class GroupProcessor(Processor):
    def __init__(self) -> None:
        self.abort_processor = AbortProcessor()
        self.start_processor = StartProcessor()

    def start(self, group: Group) -> None:
        self.start_processor.process(group)

    def abort(self, group: Group) -> None:
        self.abort_processor.process(group)
