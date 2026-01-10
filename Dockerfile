FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

COPY --from=ghcr.io/astral-sh/uv:debian /usr/local/bin/uv /usr/local/bin

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /usr/app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

RUN poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["poetry", "run", "rubrical", "grade"]
