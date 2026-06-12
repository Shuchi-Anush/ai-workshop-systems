if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not installed. Please install uv first: https://github.com/astral-sh/uv"
    exit 1
}

Write-Host "Bootstrapping AI Workshop Systems..."
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Error "uv sync failed."
    exit 1
}

if (!(Test-Path ".venv")) {
    Write-Error "Virtual environment (.venv) was not created successfully."
    exit 1
}

Write-Host "Setup complete."
Write-Host "Please use 'uv run <command>' for all executions to guarantee consistency."
