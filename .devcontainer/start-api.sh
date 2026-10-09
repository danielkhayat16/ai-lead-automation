#!/usr/bin/env bash
set -e
cd /workspaces/ai-lead-automation/backend
pkill -f "uvicorn main:app" 2>/dev/null || true
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/ai-lead-api.log 2>&1 &
echo "FastAPI started on port 8000"
