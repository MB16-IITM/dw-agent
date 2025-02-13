# Use official Python base image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libatlas3-base \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g prettier@3.4.2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV (keep existing version)
RUN pip install --no-cache-dir uv==0.5.30

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DATA_ROOT=/app/data \
    VIRTUAL_ENV=/app/venv \
    PATH="/app/venv/bin:$PATH"

# Create directory structure FIRST
RUN mkdir -p ${DATA_ROOT} && \
    chmod 755 ${DATA_ROOT}

RUN mkdir -p /data && \
    chmod 755 /data


# Create virtual environment
RUN python -m venv ${VIRTUAL_ENV}

# Set volume declaration (AFTER symlink)
VOLUME /data

WORKDIR /app

# Continue with build steps
COPY pyproject.toml uv.lock ./
RUN . ${VIRTUAL_ENV}/bin/activate && \
    uv pip install -r pyproject.toml --strict

COPY .prettierrc /app/
COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
