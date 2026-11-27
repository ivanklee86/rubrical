FROM dhi.io/python:3.14-debian13-sfw-dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install git (needed for setuptools_scm version detection)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install uv by copying the binary from the official image
COPY --from=ghcr.io/astral-sh/uv:0.13.10-debian@sha256:68732682e3d20e29651553ee502356cc5a1464177ae565edc8d07c5a3282d1a7 /usr/local/bin/uv /bin

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
