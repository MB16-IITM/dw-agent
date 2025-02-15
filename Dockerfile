# Use official Python base image
FROM python:3.12-slim

# Install system dependencies as root
RUN rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git-lfs \
        libssl3 \
        ca-certificates \
        curl \
        libatlas3-base \
        libgomp1 \
        libatomic1 \
        chromium \
        chromium-driver \
        libjpeg-dev \ 
        zlib1g-dev \   
        libwebp-dev \  
        libopenjp2-7-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Install UV (keep existing version)
RUN pip install --no-cache-dir uv==0.5.30
RUN npm install -g prettier@3.4.2

# Create non-root user and data directory
RUN useradd -m -u 1000 appuser && \
    mkdir -p /data && \
    chown appuser:appuser /data && \
    chmod 755 /data

RUN git config --global user.email "automation@dataworks.com" && \
    git config --global user.name "DataWorks Automation"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DATA_ROOT=/data \
    VIRTUAL_ENV=/app/venv \
    PATH="/app/venv/bin:$PATH"

# Add Node.js binaries to PATH
ENV PATH="/usr/local/bin:${PATH}"

# Create virtual environment as root
RUN python -m venv ${VIRTUAL_ENV}

WORKDIR /app

# Copy requirements first for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
COPY --chown=appuser:appuser .prettierrc /app/

# Install dependencies as root (system packages)
RUN . ${VIRTUAL_ENV}/bin/activate && \
    uv pip install -r pyproject.toml --strict

# Switch to non-root user
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Volume declaration (must come after ownership changes)
VOLUME /data

ENV AIPROXY_TOKEN=${AIPROXY_TOKEN}




EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
