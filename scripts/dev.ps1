if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not installed. Please run scripts/setup.ps1 or install uv first."
    exit 1
}

Write-Host "Starting Resume Analyzer API in Development Mode..."
uv run fastapi dev apps/resume-analyzer/src/apps/resume_analyzer/backend/api/main.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "API failed to start. Ensure you have run 'uv sync'."
    exit 1
}
