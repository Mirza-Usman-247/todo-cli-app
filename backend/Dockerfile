# Backend Dockerfile for Todo API
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV for faster package installation
RUN pip install uv

# Copy project files
COPY pyproject.toml README.md ./
# Copy source code (relative to build context which is backend/)
COPY ./src ./src/ # Copy from backend/src to /app/src/ in container

# Verify files were copied
RUN ls -la /app/src/ || echo "ERROR: src/ not found"

# Install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD [".venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
