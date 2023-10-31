from api.models import Coordinator
from api.processors.actions import CoordinatorCreateProcessor


class CoordinatorProcessor:
    """A Facade class providing access to actions with coordinator."""

    @staticmethod
    def create(coordinator: Coordinator) -> None:
        CoordinatorCreateProcessor(coordinator).process()
