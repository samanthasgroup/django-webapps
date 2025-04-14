from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task  # type: ignore[misc]
def sample_task() -> None:
    logger.info("The sample task just ran.")
