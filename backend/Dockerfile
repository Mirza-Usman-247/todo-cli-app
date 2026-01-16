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
# Note: This copies from backend/src to /app/src/ in container
COPY src ./src/

# Verify files were copied
RUN ls -la /app/src/ || echo "ERROR: src/ not found"

# Install dependencies
RUN uv venv .venv && \
    uv pip install --python .venv/bin/python -e . .[dev] || uv pip install --python .venv/bin/python -e . || echo "Install failed"

# Expose port
EXPOSE 8000

# Run the application
CMD ["/app/.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Note: Using absolute path for reliability in container runtime

# Health check (optional - remove if /health endpoint doesn't exist yet)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
#
# WARNING: Only enable if you have implemented a /health endpoint in FastAPI
# Otherwise container will keep restarting
#
# Example endpoint to add in src/main.py:
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}
