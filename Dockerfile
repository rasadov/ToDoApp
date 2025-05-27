# Use official Python slim image
FROM python:3.13-slim

# Build argument to control dev dependencies
ARG POETRY_ARGS="--without dev"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/opt/poetry_cache

# Set working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install $POETRY_ARGS --no-root

# Copy source code
COPY . .

# Expose the app port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]