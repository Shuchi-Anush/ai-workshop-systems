@echo off
echo ===================================================
echo     AI RESUME INTELLIGENCE PLATFORM LAUNCHER      
echo ===================================================

echo [1] Validating environment...
call uv run python apps/resume-analyzer/scripts/bootstrap_workshop.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Workshop bootstrap failed. Please check logs.
    exit /b %ERRORLEVEL%
)

echo [2] Starting Backend API...
start "AI Backend API" cmd /c "uv run uvicorn apps.resume_analyzer.backend.api.main:app --port 8081 --workers 1"

echo [3] Waiting for API to initialize...
timeout /t 5 /nobreak >nul

echo [4] Starting Streamlit Observatory...
start "AI Dashboard" cmd /c "uv run streamlit run apps/resume-analyzer/src/apps/resume_analyzer/frontend/app.py"

echo ===================================================
echo SYSTEM ONLINE.
echo API: http://localhost:8081
echo Dashboard: http://localhost:8501
echo ===================================================
pause
