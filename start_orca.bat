@echo off
title ORCA — Marine Decision Support Platform
echo ==============================================================================
echo 🌊 Starting ORCA Full-Stack Web Platform (FastAPI + Multi-Agent AI + React)
echo ==============================================================================
echo.
set PYTHONIOENCODING=utf-8

if exist "C:\Users\tidke\AppData\Local\ms-playwright-go\1.57.0" (
    set PATH=C:\Users\tidke\AppData\Local\ms-playwright-go\1.57.0;%PATH%
)

echo [1/2] Launching ORCA in your default browser...
start http://localhost:8000/

echo [2/2] Running FastAPI Multi-Agent Web Server on http://localhost:8000...
echo ------------------------------------------------------------------------------
echo Web UI:      http://localhost:8000/
echo API Docs:    http://localhost:8000/docs
echo Supabase:    Connected (byikekhtwiewlpxbuwgo.supabase.co)
echo ------------------------------------------------------------------------------
echo Press Ctrl+C to terminate.
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
