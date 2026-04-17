FROM python:3.14-slim

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies (without dev dependencies)
# Using --no-dev to exclude optional dev dependencies
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy application code
COPY ./asu/ ./asu/

# Bake the build commit into the image so the landing page can display
# it (asu/__init__.py reads ASU_VERSION from env at import time). The
# publish workflow passes this via --build-arg. ASU_ENV is left empty
# here — the *deploying* compose file is what pins "dev" / "prod".
ARG ASU_VERSION=""
ENV ASU_VERSION=${ASU_VERSION}

# Run the application
CMD uv run uvicorn --host 0.0.0.0 'asu.main:app'
