# Multi-stage build for better optimization
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv && \
    uv pip install -e .

# Production stage
FROM python:3.11-slim

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Set working directory
WORKDIR /app

# Copy application code
COPY app/ ./

# Ensure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Create data directories
RUN mkdir -p data/input data/output data/param

# Run the application
CMD ["python", "run.py"]


