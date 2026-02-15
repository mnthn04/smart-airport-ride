from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def sample_async_task(name):
    logger.info(f"Starting task for {name}")
    time.sleep(5)  # Simulate some heavy work
    logger.info(f"Finished task for {name}")
    return f"Hello {name}, task completed!"
