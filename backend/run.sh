#!/bin/bash
# Start script for AIMedical Backend (FastAPI + LangGraph + Gemini API)

cd "$(dirname "$0")/.."
source .venv/bin/activate

export PYTHONPATH=$(pwd)/backend

echo "=========================================================="
echo "🩺 Starting AIMedical Modular Monolith Application Server"
echo "URL: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "=========================================================="

python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
