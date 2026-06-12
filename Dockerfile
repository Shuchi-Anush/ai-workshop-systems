# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy the workspace configuration and lockfile
COPY pyproject.toml ./

# Copy packages and the current app codebase
# (In the future, this Dockerfile will be moved into apps/<name>/Dockerfile)
COPY packages/ packages/
COPY shared/ shared/
COPY task_01_resume_rag/ task_01_resume_rag/
COPY tests/ tests/

# Install the workspace in editable mode using uv
# We sync dependencies to ensure everything defined in pyproject.toml is installed.
# We are currently skipping the lockfile generation if it doesn't exist yet for local dev speed.
RUN uv pip install -e . || echo "Editable install skipped or failed. Run uv lock first if deploying."
RUN uv pip install pytest httpx

# Expose API port
EXPOSE 8000

# Default command for local development testing
CMD ["uv", "run", "pytest", "tests/"]
