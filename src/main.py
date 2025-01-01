from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from typing import Optional
from enum import Enum as PyEnum
import re
import requests
import redis
import os
from dotenv import load_dotenv
from celery import Celery
from pr_analysis import *
import json

load_dotenv(".env")
REDIS_URL = os.environ.get('REDIS_URL')

redis_client = redis.StrictRedis.from_url(REDIS_URL, db=0, decode_responses=True)

celery_app = Celery("celery_worker")
celery_app.config_from_object("celeryconfig")


# Enum for task status
class TaskStatus(PyEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

def validate_and_extract(url):
    # Define the regex pattern for the URL
    pattern = r"^https://github\.com/([^/]+)/([^/]+)$"
    
    # Match the pattern with the input URL
    match = re.match(pattern, url)
    
    if match:
        user = match.group(1)
        repo = match.group(2)
        return user, repo
    else:
        return None, None

# Pydantic models
class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None

# Celery task
@celery_app.task
def perform_analysis(task_id: str, code: bytes, repo_url: str, pr_number: int, github_token: Optional[str]):
    print("\nperforming analysis\n")
    redis_client.set(f"{task_id}:status", TaskStatus.IN_PROGRESS.value)
    print(f"\nsetted task : {TaskStatus.IN_PROGRESS.value}\n")

    try:
        # Generate results
        result = analyze_pr_diff(code)

        redis_client.set(f"{task_id}:result", result)
        redis_client.set(f"{task_id}:status", TaskStatus.COMPLETED.value)
    except Exception as e:
        redis_client.set(f"{task_id}:status", TaskStatus.FAILED.value)
        redis_client.set(f"{task_id}:result", str(e))
        
# FastAPI app initialization
app = FastAPI()

# Error Handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Routes
@app.post("/analyze-pr")
async def analyze_pr(data: AnalyzePRRequest):

    user, repo = validate_and_extract(data.repo_url)

    if user == None or repo == None:
        raise HTTPException(status_code=400, detail= "Invalid URL")
    
    difference_response = requests.get(
        f"https://api.github.com/repos/{user}/{repo}/pulls/{data.pr_number}",
        headers={
            "Accept": "application/vnd.github.diff",
            "Authorization": f"Bearer {data.github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    )

    # GitHub request's error handling
    if difference_response.status_code != 200 and difference_response.status_code != 201:
        detail = "Error while obtaining PR code"
        if difference_response.status_code == 404:
            detail = "Resource not found"
        raise HTTPException(status_code = difference_response.status_code, detail = detail)

    code = difference_response.content

    # Generating a task_id
    task_id = str(uuid.uuid4())

    redis_client.set(f"{task_id}:status", TaskStatus.PENDING.value)
    redis_client.set(f"{task_id}:result", "")

    perform_analysis.delay(task_id, code, data.repo_url, data.pr_number, data.github_token)

    return {"task_id": task_id}
    
@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = redis_client.get(f"{task_id}:status")
    if not status:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"task_id": task_id, "status": status}

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    status = redis_client.get(f"{task_id}:status")
    if not status:
        raise HTTPException(status_code=404, detail="Task not found.")
    if status != TaskStatus.COMPLETED.value and status != TaskStatus.FAILED.value:
        raise HTTPException(status_code=400, detail="Results not available. Task is not completed.")
    result = redis_client.get(f"{task_id}:result")
    return {
        "task_id": task_id, 
        "status": status,
        "results": json.loads(result)
    }