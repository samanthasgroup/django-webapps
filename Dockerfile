FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext \
        gcc \
        libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .
