FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install curl -y \
    && curl -sSL https://install.python-poetry.org | python - --version 1.7.1

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /usr/app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

RUN poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["poetry", "run", "rubrical", "grade"]
