if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not installed. Please run scripts/setup.ps1 or install uv first."
    exit 1
}

Write-Host "Running test suite..."
uv run pytest tests/
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed."
    exit 1
}
