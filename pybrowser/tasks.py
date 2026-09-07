import time
from celery import Celery

# Configure Redis as both Message Broker and Result Backend
celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task(bind=True)
def process_data_job(self, iterations: int):
    """Simulates a long-running background task."""
    for i in range(iterations):
        time.sleep(1)
        # Update progress state accessible via polling
        self.update_state(
            state="IN_PROGRESS",
            meta={"current": i + 1, "total": iterations}
        )
    return {"status": "Complete", "result": "Processing successful"}