# Backend Dockerfile for Todo Chatbot - Phase IV
# Production-ready FastAPI application with Python 3.13-slim and UV
# Health check endpoint: /health (FastAPI endpoint)

FROM python:3.13-slim

WORKDIR /app

# Install UV package manager
# UV is a fast Python package installer and resolver
RUN pip install --no-cache-dir uv

# Copy dependency files first (for layer caching)
COPY pyproject.toml README.md ./

# Install dependencies using UV (production only, no dev dependencies)
# --no-dev flag ensures only production dependencies are installed
RUN uv pip install --system --no-cache -e .

# Copy application source code
COPY . ./

# Create non-root user for security
# appuser with UID 1001 (matches backend contract specification)
RUN useradd --create-home --uid 1001 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Set environment variables
ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check using FastAPI /health endpoint
# Should be implemented in FastAPI application
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Start FastAPI server with uvicorn
# --host 0.0.0.0 allows external connections
# --port 8000 matches exposed port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
