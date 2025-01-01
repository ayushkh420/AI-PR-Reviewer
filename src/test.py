import json
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

from main import app

client = TestClient(app)

load_dotenv(".env")
AUTH_TOKEN = os.environ.get('AUTH_TOKEN',None)

def test_analyze_pr():
    pr_data = {
        "repo_url": "https://github.com/potpie-ai/potpie",
        "pr_number": 197,
        "github_token": AUTH_TOKEN
    }

    response = client.post(
        "/analyze-pr",
        json=pr_data
    )

    assert response.status_code == 200
    assert response.json()
    response_data = response.json()
    assert type(response_data['task_id']) == str

def test_analyze_pr_invalid_url():
    pr_data = {
        "repo_url": 123,
        "pr_number": 123,
        "github_token": None
    }

    response = client.post(
        "/analyze-pr",
        json=pr_data
    )

    assert response.status_code == 400
    detail = json.loads(response.content.decode('utf-8'))['detail'][0]
    assert detail['msg']  == f"Input should be a valid string"

def test_analyze_pr_invalid_incorret_url():
    pr_data = {
        "repo_url": "https://github.com/user/repo",
        "pr_number": 123,
        "github_token": AUTH_TOKEN
    }

    response = client.post(
        "/analyze-pr",
        json=pr_data
    )

    assert response.status_code == 404
    detail = json.loads(response.content.decode('utf-8'))['detail']
    assert detail == "Resource not found"

def test_analyze_pr_invalid_pr():
    pr_data = {
        "repo_url": "https://github.com/user/repo",
        "pr_number": None,
        "github_token": None
    }

    response = client.post(
        "/analyze-pr",
        json=pr_data
    )

    assert response.status_code == 400
    detail = json.loads(response.content.decode('utf-8'))['detail'][0]
    assert detail['msg']  == f"Input should be a valid integer"

