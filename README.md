# 🔍 AI Pr-Reviewer
An intelligent code review assistant powered by LLMs that automatically analyzes GitHub pull requests and provides detailed feedback.

## ✨ Features

- Automated code review using Llama 3.2
- Real-time analysis status tracking
- Detailed feedback on code style, potential bugs, and improvements
- Asynchronous processing for large pull requests
- RESTful API interface

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **Task Queue**: Celery with Redis
- **LLM Engine**: Llama 3.2 (via Ollama)
- **Testing**: pytest

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:
- Python 3.8 or higher
- Redis server
- Ollama (for running Llama locally)

### Installation

1. Get the code
```bash
git clone git@github.com:YourUsername/pr-analysis-tool.git
cd pr-analysis-tool
```

2. Set up the environment
```bash
# Install dependencies
pip install -r src/requirements.txt

# Configure environment variables
cp src/.env.example src/.env
# Edit src/.env with your settings
```

3. Start the services
```bash
# Start Llama
ollama run llama3.2

# Start Celery Worker
# For Windows:
celery -A main.celery_app worker --loglevel=info --pool=solo
# For Unix-based systems:
celery -A main.celery_app worker --loglevel=info

# Launch the API server
uvicorn main:app --reload
```

## 📡 API Reference

### Start PR Analysis
```http
POST /analyze-pr
```
```json
{
  "repo_url": "https://github.com/user/repo",
  "pr_number": 123,
  "github_token": "your_token"
}
```

### Check Analysis Status
```http
GET /status/{task_id}
```

### Get Analysis Results
```http
GET /results/{task_id}
```

Example response:
```json
{
    "task_id": "abc123",
    "status": "completed",
    "results": {
        "files": [{
            "name": "main.py",
            "issues": [{
                "type": "style",
                "line": 15,
                "description": "Line too long",
                "suggestion": "Break line into multiple lines"
            }]
        }],
        "summary": {
            "total_files": 1,
            "total_issues": 1,
            "critical_issues": 0
        }
    }
}
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest

# Run test suite
pytest
```

## 🗺️ Roadmap

- GitHub OAuth integration
- Real-time updates via WebSocket
- Web dashboard for results visualization
- GitHub webhook support
- Custom analysis rules configuration
- Support for additional LLM models

## 🏗️ Architecture

```mermaid
graph LR
    A[GitHub PR] --> B[FastAPI Server]
    B --> C[Celery Tasks]
    C --> D[Llama LLM]
    C --> E[Redis Cache]
    B --> E
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.