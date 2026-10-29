#!/bin/bash
# Start script for AssistantMedixa Backend (FastAPI + LangGraph )

cd "$(dirname "$0")/.."
source .venv/bin/activate

export PYTHONPATH=$(pwd)/backend

PORT=${PORT:-3038}

echo "=========================================================="
echo "🩺 Starting AssistantMedixa Modular Monolith Application Server"
echo "URL: http://localhost:${PORT}"
echo "API Documentation: http://localhost:${PORT}/docs"
echo "=========================================================="

python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT} --reload
