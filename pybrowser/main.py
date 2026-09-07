from fastapi import FastAPI, status
from pydantic import BaseModel
from tasks import process_data_job, celery_app
from celery.result import AsyncResult

app = FastAPI()

class JobRequest(BaseModel):
    iterations: int = 10

@app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
def start_job(request: JobRequest):
    """Trigger the background process and return task ID."""
    task = process_data_job.delay(request.iterations)
    return {"job_id": task.id, "status_url": f"/jobs/{task.id}"}

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Poll job status and retrieve result when finished."""
    task_result = AsyncResult(job_id, app=celery_app)
    
    if task_result.state == "PENDING":
        return {"state": task_result.state, "progress": "Job queued"}
    elif task_result.state == "IN_PROGRESS":
        return {"state": task_result.state, "details": task_result.info}
    elif task_result.state == "SUCCESS":
        return {"state": task_result.state, "result": task_result.result}
    
    return {"state": task_result.state, "error": str(task_result.info)}