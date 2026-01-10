FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv by copying the binary from the official image
COPY --from=ghcr.io/astral-sh/uv:debian /usr/local/bin/uv /usr/local/bin

WORKDIR /app

# Create an isolated virtual environment
RUN python -m venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy project metadata first for better Docker layer caching
COPY pyproject.toml ./
COPY uv.lock ./

# Install runtime dependencies only (exclude dev and skip installing the project)
RUN uv sync --no-dev --no-install-project

# Copy the application source
COPY . .

# Ensure the project itself is installed and entrypoints are available
RUN uv sync --no-dev

# Run the CLI
ENTRYPOINT ["rubrical", "grade"]
