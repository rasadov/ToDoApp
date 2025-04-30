# Use official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1

# Set working directory
WORKDIR /src

# Install system dependencies & curl (for installing Poetry)
RUN apt-get update && apt-get install -y \
    curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only the Poetry files first to cache deps
COPY pyproject.toml poetry.lock ./

# Disable virtualenvs
RUN poetry config virtualenvs.create false \
    && poetry install --with dev

# Copy source code
COPY . .

# Expose the app port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
