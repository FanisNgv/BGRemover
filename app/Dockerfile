FROM python:3.12-slim

WORKDIR /src

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR="/opt/poetry/cache" \
    PIP_CACHE_DIR="/opt/pip/cache" \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN mkdir -p $POETRY_HOME \
    && mkdir -p $POETRY_CACHE_DIR \
    && mkdir -p $PIP_CACHE_DIR

RUN --mount=type=cache,target=/opt/pip/cache \
    pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN --mount=type=cache,target=/opt/poetry/cache \
    --mount=type=cache,target=/opt/pip/cache \
    poetry install --no-root --only main --no-interaction --no-ansi

COPY ./app /src/app

ENV PYTHONPATH=/src

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 